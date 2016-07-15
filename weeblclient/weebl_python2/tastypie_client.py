from collections import MutableMapping
from copy import copy
import json
import requests
from requests.exceptions import ConnectionError
from six.moves.urllib_parse import urlsplit, urljoin
from weeblclient.weebl_python2 import utils
from weeblclient.weebl_python2.exception import (
    UnexpectedStatusCode,
    InstanceAlreadyExists,
    UnauthorisedAPIRequest,
)


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
        self._populate_resources()

    def _populate_resources(self):
        response = \
            self.requester.make_request('get', url=self.requester.make_url())
        for resource in response.json().keys():
            uri_field = self.uri_field_overrides.get(resource, 'uuid')
            client = ResourceClient(requester=self.requester,
                                    resource_name=resource,
                                    uri_field=uri_field)
            setattr(self, resource, client)


class ResourceClient(object):
    def __init__(self, requester=None, resource_name=None, uri_field='uuid'):
        self.requester = requester
        self.resource_name = resource_name
        self.uri_field = uri_field
        self.make_url = requester.make_url
        self.make_relative_url = requester.make_relative_url
        self.make_request = requester.make_request
        self.__fields = None

    @property
    def fields(self):
        if self.__fields is None:
            self.__fields = self._get_fields()
        return self.__fields

    def _get_fields(self):
        response = self.make_request(
            'get', url=self.make_url(self.resource_name, 'schema'))
        return response.json().get('fields')

    @staticmethod
    def _filterify_resource_objects(filters):
        def resourceobject_filter(key, value):
            if isinstance(value, ResourceObject):
                key = key + '__' + value.resource_client.uri_field
                value = value.uri_field_value
            # TODO: elif isinstance(value, list): ... of ResourceObjects
            return (key, value)

        filters = copy(filters)
        for key, value in filters.items():
            del filters[key]
            key, value = resourceobject_filter(key, value)
            filters[key] = value
        return filters

    def _kwargs_to_filters(self, **filters):
        filter_by = None
        if filters:
            filters = ResourceClient._filterify_resource_objects(filters)
            filter_by = '?' + "&".join(
                ["{}={}".format(k, v) for k, v in filters.items()]
            )
        return self.make_url(self.resource_name, query=filter_by)

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
        if 'meta' not in value or value['meta'].get('total_count') != 1:
            raise ValueError('Did not get one object back from request')
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
            'post', url=self.make_url(self.resource_name),
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
    def __init__(self, data=None, uri=None, resource_client=None):
        """Create a ResourceObject from a dict representation of data"""
        self.resource_client = resource_client
        self.data = data
        self.__orig = copy(data)
        self.__filled = False
        if uri is not None:
            self.__populate_from_uri(self.resource_client.make_url(uri))

    def __populate_from_uri(self, uri):
        response = self.resource_client.make_request('get', url=uri)
        self.data = response.json()
        self.__orig = copy(self.data)
        self.__filled = True

    @property
    def uri_field_value(self):
        return self.data.get(self.resource_client.uri_field)

    @property
    def resource_uri(self):
        return self.resource_client.make_relative_url(
            self.resource_client.resource_name, self.uri_field_value)

    def delete(self):
        self.resource_client.make_request('delete', url=self.resource_uri)

    def edit(self, **kwargs):
        self.data.update(kwargs)
        self.save()

    def save(self):
        if self.__orig != self.data:
            self.resource_client.make_request(
                'put', url=self.resource_uri,
                data=json.dumps(self.data, cls=ExtendedJsonEncoder))
            self.__orig = copy(self.data)

    def fill(self, force=False):
        if force or not self.__filled:
            self.__populate_from_uri(self.resource_uri)

    def __getitem__(self, key):
        if key in self.resource_client.fields:
            return self.data.get(key)
        raise ValueError('Does not have key')

    def __setitem__(self, key, value):
        if key in self.resource_client.fields:
            if not self.resource_client.fields[key]['readonly']:
                self.data[key] = value
                return
        raise ValueError('Does not have key or readonly')

    def __delitem__(self, key):
        if key in self.resource_client.fields:
            if not self.resource_client.fields[key]['readonly']:
                del self.data[key]
                return
        raise ValueError('Does not have key or readonly')

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data.keys())
