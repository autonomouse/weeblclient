from collections import MutableMapping, defaultdict
from copy import copy
import json
import yaml
import requests
from pprint import pprint
from requests.exceptions import ConnectionError
from six.moves.urllib_parse import urlsplit, urljoin
from weeblclient import utils
from weeblclient.exception import (
    UnexpectedStatusCode, InstanceAlreadyExists, UnauthorisedAPIRequest)


class ExtendedJsonEncoder(json.JSONEncoder):
    """Extended JSONEncoder to work with a ResourceObject"""
    def default(self, o):
        if isinstance(o, ResourceObject):
            return o.resource_uri
        return json.JSONEncoder.default(self, o)


class Requester(object):
    def __init__(self, base_uri, username=None, apikey=None):
        parsed_uri = urlsplit(base_uri)
        self.base_uri = parsed_uri.scheme + '://' + parsed_uri.netloc
        self.path_uri = parsed_uri.path
        self.headers = {"content-type": "application/json",
                        "limit": None}
        self.username = username
        if username is not None:
            self.headers["Authorization"] =\
                "ApiKey {}:{}".format(username, apikey)
        self.LOG = utils.get_logger("tastypie_client.Requester")

    def make_relative_url(self, *path_list, **kwargs):
        def path_join(parts):
            return '/' + "/".join([part.strip('/') for part in parts])

        path = path_join(path_list)
        if not path.startswith(self.path_uri):
            path = path_join((self.path_uri, path))
        if '?' not in path and not path.endswith('/'):
            path += '/'
        query = kwargs.get('query')
        if query is not None:
            path += query
        return path

    def make_url(self, *path_list, **kwargs):
        return urljoin(self.base_uri,
                       self.make_relative_url(*path_list, **kwargs))

    def make_request(self, method, **payload):
        payload['headers'] = self.headers
        try:
            if method == 'get':
                response = requests.get(**payload)
            elif method == 'post':
                response = requests.post(**payload)
            elif method == 'put':
                response = requests.put(**payload)
            elif method == 'delete':
                response = requests.delete(**payload)
        except ConnectionError as error:
            msg = "Could not connect to Weebl server {}:\n\n {}\n".format(
                payload['url'], error)
            self.LOG.error(msg)
            raise

        # Log payload data:
        payload.pop('headers')
        payload['response_code'] = response.status_code
        payload['request_type'] = response.request
        self.LOG.debug(payload)

        # If response code isn't 2xx:
        msg = "{} request to {} returned a status code of {}"
        err_str = 'duplicate key value violates'
        if str(response.status_code) == '401':
            msg = "{} is not authorised to make this {} request to {}.".format(
                self.username, method, payload['url'])
            raise UnauthorisedAPIRequest(msg)
        elif str(response.status_code) == '500' and err_str in response.text:
            obj = payload['url'].rstrip('/').split('/')[-2]
            msg += " - {} already exists or violates unique constraint."
            raise InstanceAlreadyExists(msg.format(
                method, payload['url'], response.status_code, obj))
        if str(response.status_code)[0] != '2':
            msg += ":\n\n {}\n"
            raise UnexpectedStatusCode(msg.format(method, payload['url'],
                                       response.status_code, response.text))
        return response


class ApiClient(object):
    def __init__(self, requester=None, uri_field_overrides=None):
        self.requester = requester
        self.uri_field_overrides = uri_field_overrides
        self.schema_lookup = {}
        self._populate_resources()
        self.endpoints = []

    def _populate_resources(self):
        self.endpoints = []
        response = \
            self.requester.make_request('get', url=self.requester.make_url())
        for name, resource in response.json().items():
            uri_field = self.uri_field_overrides.get(name, 'uuid')
            client = ResourceClient(requester=self.requester,
                                    schema=resource['schema'],
                                    endpoint=resource['list_endpoint'],
                                    api=self,
                                    uri_field=uri_field)
            self.schema_lookup[resource['schema']] = client
            self.endpoints.append(name)
            setattr(self, name, client)

    def resource_client(self, schema_url):
        return self.schema_lookup[schema_url]


class ResourceClient(object):
    def __init__(self, requester=None, schema=None, endpoint=None, api=None,
                 uri_field='uuid'):
        self.requester = requester
        self.endpoint = endpoint
        self.schema = schema
        self.uri_field = uri_field
        self.api_lookup = api
        self.make_url = requester.make_url
        self.make_relative_url = requester.make_relative_url
        self.make_request = requester.make_request
        self.__fields = None

    @property
    def fields(self):
        if self.__fields is None:
            self.__fields = self._get_fields()
        return self.__fields

    @property
    def __doc__(self):
        return pprint(self.fields)

    def _get_fields(self):
        response = self.make_request(
            'get', url=self.make_url(self.schema))
        return response.json().get('fields')

    @staticmethod
    def __clean_filter(filter_path, filter_value):
        """Convert filters with ResourceObjects to filter on their primary key,
        if given a single filter with all ResourceObjects, assume we want only
        to exactly match all and only all, by using the __mexact filter addon
        for tastypie.
        returns a tuple: (fully_specified_filter: fully_reduced_values)
            where fully_reduced_value could be a list, and fully reduced means
            to use the resourceObjects specific pk value
        """
        def urlescape(object_):
            if isinstance(object_, ResourceObject):
                object_ = object_.uri_field_value
            return requests.utils.quote(str(object_), safe='')

        def filter_key_for_object(base_key, value):
            """Given the key of a filter, if it is for a ResourceObject, append
            the correct comparator to the end of the key."""
            if isinstance(value, ResourceObject):
                base_key += '__' + value.resource_client.uri_field
            return urlescape(base_key)

        if not isinstance(filter_value, list):
            return (filter_key_for_object(filter_path, filter_value),
                    urlescape(filter_value))

        if not filter_value:  # empty list
            return (urlescape(filter_path), [])

        # we have a value that is a non-empty list at this point
        # so we'll check if we have a consistent set of objects
        full_filter = defaultdict(list)
        for val in filter_value:
            filter_ = filter_key_for_object(filter_path, val)
            if isinstance(val, ResourceObject):
                # we have a list of ResourceObjects and are passing
                # them with a single filter so use __mexact filter
                filter_ += urlescape('__mexact')
            full_filter[filter_].append(urlescape(val))
        if len(full_filter) > 1:
            raise ValueError('Passed a list of objects with different '
                             'types to create a filter: %s' % filter_value)
        return list(full_filter.items())[0]

    @staticmethod
    def _filterify_resource_objects(filters):
        cleaned_filters = set()
        for key, value in copy(filters).items():
            key, value = ResourceClient.__clean_filter(key, value)
            # flatten if the values are iterable
            if isinstance(value, list):
                cleaned_filters.update(set([(key, item) for item in value]))
            else:
                cleaned_filters.add((key, value))
        return cleaned_filters

    def _kwargs_to_filters(self, **filters):
        filter_by = None
        if filters:
            filters = ResourceClient._filterify_resource_objects(filters)
            filter_by = '?' + "&".join(
                ["{}={}".format(k, v) for k, v in filters]
            )
        return self.make_url(self.endpoint, query=filter_by)

    def objects(self, **kwargs):
        """Return all objects that match the given kwargs"""
        response = self.make_request(
            'get', url=self._kwargs_to_filters(**kwargs)).json()
        while True:
            for object_ in response.get('objects'):
                yield ResourceObject(data=object_, resource_client=self)
            if response['meta'].get('next') is None:
                break
            response = self.make_request(
                'get', url=self.make_url(response['meta']['next'])).json()

    def get(self, **kwargs):
        """Return one object"""

        response = self.make_request(
            'get', url=self._kwargs_to_filters(limit=1, **kwargs))
        value = response.json()
        if 'meta' not in value or value['meta'].get('total_count') < 1:
            raise ValueError('Did not get any objects back from request')
        elif value['meta'].get('total_count') > 1:
            raise ValueError('Got more than one object back from request')
        value = value['objects'][0]
        # check all kwargs are in returned response if we don't have related
        # data or related ('__') keys in our query
        if kwargs == ResourceClient._filterify_resource_objects(kwargs) and\
                not any(['__' in key for key in kwargs]):
            ensure_correct = copy(value)
            ensure_correct.update(kwargs)
            if value != ensure_correct:
                raise ValueError('Did not get back the object asked for')
        return ResourceObject(data=value, resource_client=self)

    def exists(self, **kwargs):
        try:
            self.get(**kwargs)
        except ValueError:
            return False
        return True

    def create(self, **kwargs):
        """Create one object"""
        response = self.make_request(
            'post', url=self.make_url(self.endpoint),
            data=json.dumps(kwargs, cls=ExtendedJsonEncoder))
        return ResourceObject(data=response.json(), resource_client=self)

    def get_or_create(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ValueError:
            return self.create(**kwargs)

    def delete(self, **kwargs):
        """Delete all objects that match the given kwargs"""
        self.make_request('delete', url=self._kwargs_to_filters(**kwargs))


class ResourceObject(MutableMapping):
    def __init__(self, data=None, uri=None, resource_client=None, load=True):
        """Create a ResourceObject from a dict representation of data"""
        self.resource_client = resource_client
        self._data = data
        self.__orig = copy(data)
        self.__override_resource_uri = uri
        if load:  # only load if we are not given the data already
            self.populate()
        self.__resourcify_children()
        yaml.add_representer(ResourceObject, ResourceObject.to_yaml)
        yaml.SafeDumper.add_representer(ResourceObject, ResourceObject.to_yaml)

    def __resourcify_children(self):
        """If we get back some full entries for children, they will just be the
        data without ResourceObject wrappers around them, we fix that here."""
        def resourcify(data, schema):
            resource_client = self.resource_client.api_lookup.resource_client(
                schema)
            if isinstance(data, dict):
                return ResourceObject(
                    data=data, uri=None, resource_client=resource_client,
                    load=False)
            else:
                return ResourceObject(
                    data=None, uri=data, resource_client=resource_client,
                    load=False)

        if not self._data:
            return
        for key in self._data:
            field_data = self.resource_client.fields.get(key)
            if field_data is None:
                schema = self.resource_client.schema
                resource = schema.split('/schema')[0].split('/')[-1]
                raise ValueError(
                    "{} not a valid field in {}, add a field server-side to "
                    "the {} resource in this instance of weebl"
                    .format(key, schema, resource))
            if self._data[key] is None:
                continue
            if field_data['type'] == 'related':
                schema_url = field_data['related_schema']
                if field_data['related_type'] == 'to_many':
                    self._data[key] = [resourcify(item, schema_url)
                                       for item in self._data[key]]
                else:
                    self._data[key] = resourcify(self._data[key], schema_url)

    def populate(self, force=False, resourcify=False):
        if force or not self._data:
            response = self.resource_client.make_request(
                'get', url=self.resource_client.make_url(self.resource_uri))
            self._data = response.json()
            self.__orig = copy(self._data)
            if resourcify:
                self.__resourcify_children()

    @property
    def uri_field_value(self):
        return str(self.__orig.get(self.resource_client.uri_field))

    @property
    def resource_uri(self):
        if self.__override_resource_uri:
            return self.__override_resource_uri
        return self.resource_client.make_relative_url(
            self.resource_client.endpoint, self.uri_field_value)

    def delete(self):
        self.resource_client.make_request(
            'delete', url=self.resource_client.make_url(self.resource_uri))

    def break_all_relations(self):
        for field, content in self.resource_client.fields.items():
            if content['type'] == 'related' and not content['readonly']:
                if content['related_type'] == 'to_many':
                    self[field] = []
                else:
                    self[field] = None
        self.save()

    def edit(self, **kwargs):
        self._data.update(kwargs)
        self.save()

    def save(self):
        if self.__orig != self._data:
            self.resource_client.make_request(
                'put', url=self.resource_client.make_url(self.resource_uri),
                data=json.dumps(self._data, cls=ExtendedJsonEncoder))
            self.__orig = copy(self._data)

    def __repr__(self):
        return "ResourceObject(%s, '%s')" % (str(self._data),
                                             self.resource_uri)

    def __str__(self):
        return repr(self)

    @staticmethod
    def to_yaml(dumper, obj):
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', obj.data)

    @property
    def data(self):
        if not self._data:
            return self.resource_uri
        safe_data = {}
        for key, value in self._data.items():
            if isinstance(value, ResourceObject):
                value = value.data
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, ResourceObject):
                        item = item.data
                    new_list.append(item)
                value = new_list
            safe_data[key] = value
        return safe_data

    def __getitem__(self, key):
        self.populate()
        if key in self.resource_client.fields:
            return self._data.get(key)
        raise ValueError('Does not have key')

    def __setitem__(self, key, value):
        self.populate()
        if key in self.resource_client.fields:
            if not self.resource_client.fields[key]['readonly']:
                self._data[key] = value
                return
        raise ValueError('Does not have key or readonly')

    def __delitem__(self, key):
        self.populate()
        if key in self.resource_client.fields:
            if not self.resource_client.fields[key]['readonly']:
                del self._data[key]
                return
        raise ValueError('Does not have key or readonly')

    def __len__(self):
        self.populate()
        return len(self._data)

    def __iter__(self):
        self.populate()
        return iter(self._data.keys())

    def __eq__(self, other):
        # Only compares that the resource_uri is the same (that we are pointing
        # at the same remote object) for comparisons in lists/otherwise where
        # the data gotten from serverside requests may not be filled out the
        # same but they are references to the same object.
        return isinstance(other, ResourceObject) and \
            self.resource_uri == other.resource_uri
