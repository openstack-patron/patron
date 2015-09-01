__author__ = 'root'

from novaclient import client
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

nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
print nova.patrons.verify("compute_extension:admin_actions")