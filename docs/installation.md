# Install weeblclient

It is packaged as a deb package in one of the oil-ci owned ppas:

* [https://launchpad.net/~oil-ci/+archive/ubuntu/integration](integration)
* [https://launchpad.net/~oil-ci/+archive/ubuntu/staging](staging)
* [https://launchpad.net/~oil-ci/+archive/ubuntu/production](production)

So add one of the ppas (since they are private you will need to get your credentials):
Go to your [https://launchpad.net/~/+archivesubscriptions](private ppa credentials) and click on "view" for the appropriate archive

Copy the deb and deb-src lines to /etc/apt/sources.list

```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 2AE6E4C0 # (the public key for all oil-ci owned repos)
sudo apt update
sudo apt install python-weeblclient
```
