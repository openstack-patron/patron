import re
from pprint import pprint
op_map = {}

def parse_five_keys(test):
	#print test
	key_calls = {"servers": "nova.objects.instance.Instance.get_by_uuid(uuid)",
             "os-interface": "nova.objects.virtual_interface.VirtualInterface.get_by_uuid(uuid)",
             "os-keypairs": "nova.objects.keypair.KeyPair.get_by_name(user_id, name)",
			 "os-agents": "",
             "os-aggregates": "nova.objects.aggregate.Aggregate.get_by_id(id)",
             "os-networks": "nova.network.neutronv2.api.API.get(id)", # "nova.objects.network.Network.get_by_id(uuid)"
             "os-tenant-networks": "nova.network.neutronv2.api.API.get(id)",
             "os-quota-sets": "nova.quota.QUOTAS.get_project_quotas(id)",
             "os-simple-tenant-usage": "nova.api.patron_verify.PatronVerify.get_tenant_by_id(id)",
             "os-instance-actions": "", # although "instance_action" has its own object, we still use "instance" as the object here
             "os-hosts": "nova.compute.api.HostAPI.instance_get_all_by_host(name)",
             "os-hypervisors": "nova.compute.api.HostAPI.compute_node_search_by_hypervisor(name)",
             "os-security-groups": "nova.objects.security_group.SecurityGroup.get(id)",
             "os-server-groups": "nova.objects.instance_group.InstanceGroup.get_by_uuid(uuid)",
			 "os-floating-ips":"",
			 "os-security-group-rules":"",
             "os-migrations": "nova.objects.migraton.Migration.get_by_id(id)",
		     "os-extra_specs":"",
			 "os-instance_usage_audit_log": "",
             "flavors": "nova.objects.flavor.Flavor.get_by_id(id)",
             "images": "",
             "volumes": ""
             }
	key_ids = {}

	str_inner_action = ''
	#test = "req_port = 8774, req_api_version = u'/v2', req_method = 'POST', req_path_info = u'/df1d1e97c4f54e5a8d790d4684c3fa2a/servers/detail', req_inner_action = u''"
	five_key_pattern = re.compile("req_port = (.*), req_api_version = u'(.*)', req_method = '(.*)', req_path_info = u'(.*)', req_inner_action = (u'.*'),")
	# port_pattern = re.compile("req_port = (.*), req_api_version")
	# version_pattern = re.compile(".*req_api_version = (.*), req_method.*")
	# method_pattern = re.compile(".*req_method = (.*), req_path.*")
	# inner_action_pattern = re.compile(".*req_inner_action = (.*), op=")
	# path_info_pattern = re.compile(".*req_path_info = (.*), req_inner.*")
	id_pattern = "[0-9a-f]{32}"
	uuid_pattern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
	value_pattern = "=([^&]*)(&|$)"
	match = re.match(five_key_pattern, test)
	if match != None:
		port = match.group(1)
		version = match.group(2)
		method = match.group(3)
		path_info = match.group(4)
		inner_action = match.group(5)

		if path_info.startswith('u'):
			path_info = path_info[2:len(path_info)-1]
		path_info_list = path_info.strip('/').split('/')
		#print path_info_list
		if len(path_info_list) > 0:
			if re.match(id_pattern, path_info_list[0]) != None:
				path_info_list[0] = "%ID%"
			elif re.match(uuid_pattern, path_info_list[0]) != None:
				path_info_list[0] = "%UUID%"
			else:
				path_info_list[0] = "%NAME%"
		for i in range(len(path_info_list) - 1):
			if path_info_list[i] in key_calls and path_info_list[i+1] != "detail":
				key_ids[path_info_list[i]] = path_info_list[i+1]
				if re.match(id_pattern, path_info_list[i+1]) != None:
					path_info_list[i+1] = "%ID%"
				elif re.match(uuid_pattern, path_info_list[i+1]) != None:
					path_info_list[i+1] = "%UUID%"
				else:
					path_info_list[i+1] = "%NAME%"
		temp = "/" + "/".join(path_info_list)
		temp = re.sub(value_pattern, "=%VALUE%", temp)
		temp = temp.strip("&")
		str_path_info = temp


		if inner_action == '':
			str_inner_action = ""
		elif str_path_info.endswith("action"):
			inner_action_pattern1 = re.compile("u'{\"([A-Za-z]*)\":")
			m = re.search(inner_action_pattern1, inner_action)
			if m != None:
				inner_action = m.group(1)
				str_inner_action = inner_action
		else:
			str_inner_action = ""
		five_key_tuple = (int(port), version, str_path_info, method, str_inner_action)
		#print five_key_tuple
		return five_key_tuple
	else:
		return None

# parse op
def op_parse(string):
	op_pattern = re.compile("'(.*)'\n2015-10-25.*", re.S)
	m = re.match(op_pattern, string)
	if m != None:
		return m.group(1)


#runtime result
def rs_parse(string):
	#print string
	rs = []
	rs_pattern = re.compile(".*Response - Headers: {'status': '([0-9]{3})', 'content-length.*", re.S)
	time_pattern = re.compile(".* ([0-9]{1}.[0-9]{3}s)\n", re.S)
	m = re.match(rs_pattern, string)
	m1 = re.match(time_pattern, string)
	#print m.group(1)
	if m != None:
		rs.append(m.group(1))
	if m1 != None:
		rs.append(m1.group(1))
	return rs

# write results in file in line

def do_write(num, five_key_tuple, result, time):
	f = open('/var/log/tempest/nova-op.log','a+')
	f.write("\nno : %r\nfive_key : %r\nresult : %r\ntime : %r\n" % (num, five_key_tuple,result, time))
	f.close

# write op mapping
# def do_write_opmap():
# 	f = open('/var/log/tempest/nova-op-map.log','a+')
# 	for k,v in op_map.items():
# 		f.write("%r : %r\n" % (k,v))
# 	f.close()

def do_write_time(a):
	f = open('/var/log/tempest/nova-op.log','a+')
	f.write("\n\n----------------------------------------------------------------\n\n")
	f.write("total time : %rs" % a)
	f.close()

# core parser
def core_parse():
	t = ''
	total = 0
	result0 = ''
	five_key_tuple = ()
	f = open('/var/log/tempest/tempest.log')
	STRING = f.read()
	lists = STRING.split("### ")

	for i in range(1,len(lists)):
		print lists[i]
		ops = []
		if lists[i].find("op=2015") != -1:
			# five keys
			test = lists[i].split("op=")[0]
			if parse_five_keys(test) != None:
				five_key_tuple1 = parse_five_keys(test)

			# op
			ops_tuple1 = ()
			#runtime result
			tmp = lists[i].split("op=")[1]
			result = rs_parse(tmp)
			if len(result) > 1:
				t1 = result[1]
				each_time = result[1][0:len(result[1])-1]
				each_time = float(each_time)
				total = total + each_time
			if len(result) > 0:
				if result[0] == '200' or result[0] == '204' or result[0] == '202':
					result0 = "Permited"
				elif result[0] == '403':
					result0 = 'Denied'
				else:
					result0 = "HttpCode : " + result[0]
			do_write(i, five_key_tuple1, result0, t1)
			op_map[five_key_tuple1] = ops_tuple1

		elif lists[i].find("$") != -1:
			#five keys
			test = lists[i].split("$")[0]
			if parse_five_keys(test) != None:
				five_key_tuple = parse_five_keys(test)
			#op
			tmp = lists[i].split("$ ")
			l = len(tmp)

			if l>2:
				for j in range(1,l-1):
					tmp[j] = tmp[j].strip()
					tmp[j] = tmp[j].strip('\n')
					tmp[j] = tmp[j].strip("'")
					ops.append(tmp[j])
			tmp[-1] = tmp[-1].strip()
			ops.append(op_parse(tmp[-1]))
			ops_tuple = tuple(ops)
			#runtime result
			result = rs_parse(tmp[-1])
			if len(result) > 1:
				t = result[1]
				each_time = result[1][0:len(result[1])-1]
				each_time = float(each_time)
				total = total + each_time
			if len(result) > 0:
				if result[0] == '200' or result[0] == '204' or result[0] == '202':
					result0 = "Permited"
				elif result[0] == '403':
					result0 = 'Denied'
				else:
					result0 = "HttpCode : " + result[0]
			do_write(i, five_key_tuple, result0, t)
			op_map[five_key_tuple] = ops_tuple



	pprint(op_map)
	do_write_time(total)

core_parse()