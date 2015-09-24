#Add by Yang Luo

"""
Used to test Patron API's verify method.

"""

from patronclient import client
import socket

if socket.gethostname() == "controller":
    VERSION = "2"
    USERNAME = "admin"
    PASSWORD = "123456"
    PROJECT_ID = "admin"
    AUTH_URL = "http://controller:5000/v2.0/"
else :
    VERSION = "2"
    USERNAME = "admin"
    PASSWORD = "123"
    PROJECT_ID = "admin"
    AUTH_URL = "http://ly-controller:5000/v2.0/"

cli = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL, service_type="access")
response = cli.patrons.verify(json = {'op': "compute_extension:admin_actions"})
print response
if response[1]['res'] == True:
    print "Access permitted."
else:
    print "Acess denied."
