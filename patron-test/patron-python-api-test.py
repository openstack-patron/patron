__author__ = 'root'

VERSION = "2"
USERNAME = "demo"
PASSWORD = "123"
PROJECT_ID = "demo"
AUTH_URL = "http://ly-controller:5000/v2.0/"


from novaclient import client
nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
print nova.patron_access.do_verify()


# from keystoneclient.auth.identity import v2
# from keystoneclient import session
# from novaclient import client
# auth = v2.Password(auth_url=AUTH_URL,
#                        username=USERNAME,
#                        password=PASSWORD,
#                        tenant_name=PROJECT_ID)
# sess = session.Session(auth=auth)
# nova = client.Client(VERSION, session=sess)
# print nova.servers.list()