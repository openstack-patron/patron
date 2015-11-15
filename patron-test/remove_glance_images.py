import re
import os

m = os.popen("glance image-list")
m_s = m.read()
print m_s
p = re.compile("[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", re.S)
lists = p.findall(m_s)
#print lists
for i in lists:
	name = os.popen("glance image-show %s" % i).read()
	print name
	if "cirros" in name:
		print "Do not delete cirros!"
	else:
		os.popen("glance image-delete %r" % i)	
		print ("Deleted one image %s!" % i)

