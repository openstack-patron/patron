#!/usr/bin/python
import base64,urllib,httplib,json,os
from urlparse import urlparse
 
#dst_url="access_control_verify/%(user_id)s/resources/%(res_id)s/action/%(action)s/"

url1="controller:5000"
params1 = '{"auth": {"tenantName": "demo", "passwordCredentials": {"username": "demo", "password": "123456"}}}'
headers1 = {"Content-Type": 'application/json'}
conn1 = httplib.HTTPConnection(url1)
conn1.request("POST","/v2.0/tokens",params1,headers1)
response1 = conn1.getresponse()
data1 = response1.read()
dd1 = json.loads(data1)
conn1.close()
 
apitoken = dd1['access']['token']['id']
apitenant= dd1['access']['token']['tenant']['id']
apiurl = dd1['access']['serviceCatalog'][1]['endpoints'][0]['publicURL']
apiurlt = urlparse(dd1['access']['serviceCatalog'][1]['endpoints'][0]['publicURL'])

print dd1['access']['serviceCatalog'][1]['endpoints'][0]['publicURL'] 

url2 = apiurlt[1]
params2 = urllib.urlencode({})
#print url2, "%s/os-patron-access/123/resource/456/action/verify" % apiurlt[2], '\n'
headers2 = { "X-Auth-Token":apitoken, "Content-type":"application/json" }
conn2 = httplib.HTTPConnection(url2)
conn2.request("GET", "%s/os-patron-access/verify" % apiurlt[2], params2, headers2)
response2 = conn2.getresponse()
data2 = response2.read()

print data2

print 'cat /var/log/patron/mylog.txt'
f = open('/var/log/patron/mylog.txt', "r")
for k in f :
    print k

k = raw_input("delete mylog.txt[y/n]:")
if k=="y":
    os.remove('/var/log/patron/mylog.txt')

#dd2 = json.loads(data2)
conn2.close()
#for i in range(len(dd2['servers'])):
#    print dd2['servers'][i]['name']



##!bin/sh
#curl -s -X POST http://controller:5000/v2.0/tokens -H "Content-Type: application/json" -d '{"auth": {"tenantName": "'"$OS_TENANT_NAME"'", "passwordCredentials":{"username": "'"$OS_USERNAME"'", "password": "'"$OS_PASSWORD"'"}}}' | python -m json.tool

#curl -s -H "X-Auth-Token:fa3d4fcd450949178d81737d915569a8" http://controller:8774/v2/2cc6dbdc1c714807a931165d0cbe0e3b/resources | python -m json.tool
