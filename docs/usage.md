# Using the tastypieclient

This will connect to a server running the tastypie rest framework (http://tastypieapi.org/) and allow us to perform all actions that are exposed via the schema for each endpoint.

Assuming you have installed the client via the install guide lets get started!

You will need to know your USERNAME and APIKEY, please ask someone in #oil-devel how to get them from a server ;)

These commands will build on each other, so best do this all in one ipython session.

## Set your credentials
```
UUID = '<uuid>' # the uuid of the environment you are connecting to, so you don't do silly things
ENV_NAME = '<environment name>' # the name of the environment, so you don't do silly things
USERNAME = '<my username>' # derived from your launchpad account
APIKEY = '<apikey>' # a 40-char length alphanumeric server-generated nonce
```

## Connect to the server
```
from weeblclient.weebl_python2.weebl import Weebl

weebl = Weebl(uuid, env_name, username=USERNAME, apikey=APIKEY, weebl_url="http://10.245.0.14")
client = weebl.resources
```

If you didnt get any errors, you have successfully connected to the server! Hooray!


Now lets take our rest api for a spin...

## List the endpoints
```
client.endpoints
```

## Get all the objects from an endpoint
```
for object_ in client.productundertest.objects():
    print(object_)

```
## Query objects from an endpoint
```
for sdn in client.productundertest.objects(producttype__name='sdn'):
    print(sdn)

# or a more complicated query

for sdn in client.productundertest.objects(producttype__name='sdn', report__isnull=False, vendor__name='Metaswitch'):
    print(sdn)
```
You might have noticed this uses similar syntax to [https://docs.djangoproject.com/en/1.10/topics/db/queries/#retrieving-specific-objects-with-filters](django ORM) (which we are using on the backend).
For the database, you can traverse over tables that have a foreign key mapping using '\_\_' between the table names, followed at last by the column name, and then again an optional [https://docs.djangoproject.com/en/1.10/ref/models/querysets/#field-lookups](field lookup) that defaults to '\_\_exact'.
## Get a single object from an endpoint
```
nuage_product = client.productundertest.get(name='neutron-nuage')
# and lets get some info from it
print(nuage_product.keys())
print(nuage_product['vendor']['name'])
print(nuage_product['uuid'])
# yes you can traverse across tables here to get whatever you want
```
In addition to the 'objects' and 'get' methods, there are also a few more helpful ones that take similar parameters:

* exists
* create
* get_or_create
* delete

It should be noted that deletes are cascading deletes, so be careful when using them!!!
# Now that we know how to get some objects lets make a new one!

```
super_product = client.productundertest.create(name='super test product') # create a productundertest with a PUT to the server
super_product['vendor'] = client.vendor.get_or_create(name='super vendor') # create a vendor with a PUT to the server and set it locally to vendor
super_product.save() # make a PUT to the server to update the already existing object

client.productundertest.get(vendor__name='super vendor')

# we can also change data on traversed tables too!

super_product['vendor']['name'] = 'different'
super_product['vendor'].save()

# as this will now raise an error
client.productundertest.get(vendor__name='super vendor')
# but this will return what we want
client.productundertest.get(vendor__name='different')

# now we can delete our test objects
super_product.delete() # and since it is cascading it will delete the vendor too, if we don't want to do that we can

super_product.break_all_relations() # which will set all relations to 'None' for an object, then we can safely delete just it
super_product.delete() # be aware the break_all_relations isn't super well tested at this point, so be careful
```
