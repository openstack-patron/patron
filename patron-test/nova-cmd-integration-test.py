#Written by veotax.

import re
import os
import time
import subprocess
from pprint import pprint
import socket

service_name = "nova"

# RE to get execution time.
re_run_time = re.compile('Command run time is: (.*) seconds')

# REs to extract errors.
re_http_error = re.compile('(.*)ERROR(.*)\(HTTP (.*)\) \((.*)')
re_usage_error = re.compile('(.*)usage:(.*)')
re_bash_error = re.compile('(.*)bash(.*)line(.*)syntax error(.*)')
re_cmd_error = re.compile('ERROR \((.*)\):')
re_error = re.compile('(.*)ERROR:(.*)')

# RE to add "--debug" to original command.
re_add_debug = re.compile('^nova')
add_debug_replace_str = "nova --debug"

# RE to get path_info.
re_get_path_info = re.compile('.*REQ: curl -g -i -X (.*) http://[0-9a-zA-Z-]*:([0-9]*)(/[0-9v]*)(/[0-9a-zA-Z-/\?&_=.:]*) -H \"User-Agent: python-' + service_name + 'client\"(?:.* -d \'(.*)\')?')

# RE about created ID retrieval and reuse.
id_pattern = "[0-9a-f]{32}"
uuid_patern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
re_get_creative_macro = re.compile('-create (\$[A-Z_]*)')
re_get_created_id = re.compile('\| (' + uuid_patern + ') \|')

######################################################################
# Explanation for "answer" field:
# Permitted:        the command is permitted by access controls
# Denied:           the command is denied by access controls, the same with HTTP 403 error
# HTTP 400 Error:   ERROR (BadRequest): Compute service of ly-compute1 is unavailable at this time. (HTTP 400)
# HTTP 404 Error:   ERROR (NotFound): No instances found for any event (HTTP 404)
# HTTP 409 Error:   ERROR (Conflict): Key pair 'key1' already exists. (HTTP 409)
# HTTP 412 Error:   ERROR (ClientException): Unknown Error (HTTP 412), this error is actually because path_to_op fails to find an op
# HTTP 413 Error:   ERROR (OverLimit): Over limit (HTTP 413), this error is actually because op tuple returned by path_to_op is empty
# HTTP 422 Error:   ERROR (ClientException): Unable to process the contained instructions (HTTP 422)
# HTTP 500 Error:   ERROR (ClientException): The server has either erred or is incapable of performing the requested operation. (HTTP 500)
# HTTP 501 Error:   ERROR (HTTPNotImplemented): Unable to get dns domain (HTTP 501)
# HTTP 503 Error:   ERROR (ClientException): Create networks failed (HTTP 503)
# Command Error:    ERROR (CommandError): No image with a name or ID of 'demo-image1' exists.
######################################################################

# Debug log file path.
debuglog_file_object = open('/root/cmd-integration-test-debuglog.txt', 'w')

# Preset macros for separate machines.
if socket.gethostname() == "controller":
    macros_to_replace = {
    }
else: # "ly-controller"
    macros_to_replace = {
        "$NET_ID": "7416c4f4-5718-4c41-81df-b9eeb3c7ff41", # "demo-net"
        "$KEY_NAME": "key1",
        "$INSTANCE_NAME": "demo-instance2",
        "$HOSTNAME": "ly-compute1",
        "$AGGRE_NAME": "aggregate1",
        "$SERVER_NAME": "ly-compute1",
        "$NEW_INSTANCE_NAME": "demo-instance1-new",
        "$SERVER_GROUP_NAME": "server-group1",
        "$TENANT_NETWORK_NAME": "tenant-network1",
        "$TENANT_NETWORK_ID": "7416c4f4-5718-4c41-81df-b9eeb3c7ff41", # "demo-net"
        "$DEMO_TENANT_ID": "b52703a841604021902133822c9496e1"
    }

# Mappings and functions used to get template path info.
key_calls = {"servers": "nova.objects.instance.Instance.get_by_uuid(uuid)",
             "os-interface": "nova.objects.virtual_interface.VirtualInterface.get_by_uuid(uuid)",
             "os-keypairs": "nova.objects.keypair.KeyPair.get_by_name(user_id, name)",
             "os-aggregates": "nova.objects.aggregate.Aggregate.get_by_id(id)",
             "os-networks": "nova.network.neutronv2.api.API.get(id)", # "nova.objects.network.Network.get_by_id(uuid)"
             "os-tenant-networks": "nova.network.neutronv2.api.API.get(id)",
             "os-quota-sets": "nova.quota.QUOTAS.get_project_quotas(id)",
             "os-simple-tenant-usage": "nova.api.patron_verify.PatronVerify.get_tenant_by_id(id)",
             "os-instance-actions": "", # although "instance_action" has its own object, we still use "instance" as the object here
             "flavors": "nova.objects.flavor.Flavor.get_by_id(id)",
             "images": "",
             "volumes": ""
             }
key_ids = {}

def get_template_path_info(req_path_info):
    global key_calls
    global key_ids
    id_pattern = "[0-9a-f]{32}"
    uuid_patern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    path_info_list = req_path_info.strip("/").split("/")
    if len(path_info_list) > 0:
        key_ids["project_id"] = path_info_list[0]
        if re.match(id_pattern, path_info_list[0]) != None:
                path_info_list[0] = "%ID%"
        elif re.match(uuid_patern, path_info_list[0]) != None:
            path_info_list[0] = "%UUID%"
        else:
            path_info_list[0] = "%NAME%"

    for i in range(len(path_info_list) - 1):
        if path_info_list[i] in key_calls and path_info_list[i + 1] != "detail":
            key_ids[path_info_list[i]] = path_info_list[i + 1]
            if re.match(id_pattern, path_info_list[i + 1]) != None:
                path_info_list[i + 1] = "%ID%"
            elif re.match(uuid_patern, path_info_list[i + 1]) != None:
                path_info_list[i + 1] = "%UUID%"
            else:
                path_info_list[i + 1] = "%NAME%"
    template_path_info = "/" + "/".join(path_info_list)
    return template_path_info

remove_macro_pattern = ""
for k in macros_to_replace:
    remove_macro_pattern += ("\\" + k + "|")
remove_macro_pattern = remove_macro_pattern[:-1]

re_remove_macro = re.compile(remove_macro_pattern)

def add_macro_to_replace(macro_name, macro_value):
    # Update the RE macro.
    global remove_macro_pattern
    global re_remove_macro
    global macros_to_replace
    remove_macro_pattern += ("|\\" + macro_name)
    re_remove_macro = re.compile(remove_macro_pattern)
    # Update the map.
    macros_to_replace[macro_name] = macro_value

# text will be something like this:
# root@controller:~# nova server-group-create server-group1 "affinity"
# +--------------------------------------+---------------+---------------+---------+----------+
# | Id                                   | Name          | Policies      | Members | Metadata |
# +--------------------------------------+---------------+---------------+---------+----------+
# | ae318dd3-29a3-4f5d-96e8-9e46785df4b8 | server-group1 | [u'affinity'] | []      | {}       |
# +--------------------------------------+---------------+---------------+---------+----------+
def get_created_id(text):
    re_res = re_get_created_id.search(text)
    if re_res != None:
        return re_res.group(1)
    else:
        return None

# cmd is something like:
# nova server-group-create $SERVER_GROUP_NAME "affinity"
def get_creative_macro(cmd):
    if cmd.startswith("nova server-group-create"):
        re_res = re_get_creative_macro.search(cmd)
        if re_res != None:
            return re_res.group(1)
        else:
            return None

def macro_replace_callback(matchobj):
    if matchobj.group(0) in macros_to_replace:
        return macros_to_replace[matchobj.group(0)]
    return "!Re Replace Error!"

def get_macro_removed_command(cmd):
    return re_remove_macro.sub(macro_replace_callback, cmd)

def init_test_cases_from_script(start_line=0, end_line=99999):
    file_object = open('/usr/lib/python2.7/dist-packages/patron-test/' + service_name + '-cmd-test.sh', 'r')
    lines = file_object.readlines()
    file_object.close()

    test_cases = []

    line_cnt = 0
    cnt = 0
    for line in lines:
        line_cnt = line_cnt + 1
        if line_cnt < start_line or line_cnt >= end_line:
            continue
        if re.match("^" + service_name, line):
            cnt = cnt + 1
            line=line.strip('\n')
            test_case = {}
            test_case["no"] = cnt
            test_case["line-no"] = line_cnt
            test_case["command"] = line
            test_case["user"] = "admin"
            test_cases.append(test_case)

    return test_cases

def init_test_cases_example2():
    test_cases = []

    test_case = {}
    test_case["no"] = 1
    test_case["line-no"] = 1
    test_case["command"] = "nova dns-domains"
    test_case["user"] = "admin"
    test_cases.append(test_case)

    return test_cases

def init_test_cases_example():
    test_cases = []

    # Error
    test_case = {}
    test_case["no"] = 1
    test_case["line-no"] = 1
    test_case["command"] = "nova flavor-list"
    test_case["user"] = "admin"
    test_cases.append(test_case)

    # Permitted
    test_case = {}
    test_case["no"] = 2
    test_case["line-no"] = 2
    test_case["command"] = "nova list"
    test_case["user"] = "admin"
    test_cases.append(test_case)

    # Denied
    test_case = {}
    test_case["no"] = 3
    test_case["line-no"] = 3
    test_case["command"] = "nova service-list"
    test_case["user"] = "demo"
    test_cases.append(test_case)

    return test_cases

# Wrap the command using expect like belows if it is a "nova root-password" command:
# expect <<- DONE
# spawn nova root-password demo-instance1
# expect "New password: "
# send -- "123\r"
# expect "Again: "
# send -- "123\r"
# expect eof
# DONE
def wrap_command(cmd):
    if cmd.startswith("nova root-password") or cmd.startswith("nova --debug root-password"):
        return 'expect <<- DONE\nspawn ' + cmd + '\nexpect "New password: "\nsend -- "123\r"\nexpect "Again: "\nsend -- "123\r"\nexpect eof\nDONE'
    if cmd.startswith("nova x509-get-root-cert") or cmd.startswith("nova --debug x509-get-root-cert"):
        os.system('rm ./cacert.pem')
        return cmd
    else:
        return cmd

def get_all_from_testcase(test_case):
    test_case["creative_macro"] = get_creative_macro(test_case["command"])
    test_case["command"] = get_macro_removed_command(test_case["command"])
    debug_command = re_add_debug.sub(add_debug_replace_str, test_case["command"])
    mytask = subprocess.Popen("exec bash -c 'source /root/" + test_case["user"] + "-openrc.sh;" + wrap_command(debug_command) + "'", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    response = mytask.stdout.read()

    # Uncommented it to see the real response.
    # print response
    debuglog_file_object.write("***************************\n")
    debuglog_file_object.write("no: %s\n" % test_case["no"])
    debuglog_file_object.write(response)
    debuglog_file_object.write("\n\n")

    # Get the time.
    re_res = re_run_time.search(response)
    if re_res != None:
        seconds = re_res.group(1)
    else:
        seconds = "N/A"
    test_case["time"] = seconds

    # Get the answer.
    while True:
        # HTTP Error check.
        re_res = re_http_error.search(response)
        if re_res != None:
            http_error = re_res.group(3)
            if http_error != "403":
                answer = "HTTP " + http_error + " Error"
                break
            else:
                answer = "Denied"
                break

        # Usage Error check.
        if re_usage_error.match(response):
            answer = "Usage Error"
            break

        # Bash Syntax Errors check.
        if re_bash_error.match(response):
            answer = "Bash Error"
            break

        # Command Errors check.
        re_res = re_cmd_error.search(response)
        if re_res != None:
            cmd_error = re_res.group(1)
            answer = cmd_error
            break

        # Other Errors check.
        if re_error.match(response):
            answer = "Other Errors"
            break

        answer = "Permitted"
        break
    test_case["answer"] = answer

    # Get the path_info.
    re_ress = re_get_path_info.findall(response)
    if re_ress != None:
        test_case["path_info"] = []
        if len(re_ress) != 0:
            for re_res in re_ress:
                try:
                    # print "abcd: " + re_res.group(0)
                    path_info_tuple = (int(re_res[1]), re_res[2], get_template_path_info(re_res[3]), re_res[0], re_res[4])
                except IndexError:
                    path_info_tuple = (int(re_res[1]), re_res[2], get_template_path_info(re_res[3]), re_res[0], "")
                test_case["path_info"].append(path_info_tuple)
        else:
            test_case["path_info"].append("Failed to find!!")
    else:
        test_case["path_info"] = []
        test_case["path_info"].append("Failed to find!!")

    # Added the created id to macros_to_replace.
    if test_case["creative_macro"] != None:
        test_case["created_id"] = get_created_id(response)
        if test_case["created_id"] != None:
            add_macro_to_replace(test_case["creative_macro"].replace("NAME", "ID"), test_case["created_id"])
        else:
            print "Error: Created_ID not found!!"

    print_test_case(test_case)

def do_the_test(test_cases):
    for test_case in test_cases:
        get_all_from_testcase(test_case)

def print_test_case(test_case):
    s = 'no: %-5s    line-no: %-5s    cmd: %-65s    user: %-5s    answer: %-15s    time: %-5s    path_info: %-50s' %\
        (test_case["no"], test_case["line-no"], test_case["command"], test_case["user"], test_case["answer"], test_case["time"], test_case["path_info"][0])
    print s
    path_info_pos = s.find("path_info: (") + len("path_info: ") - 1
    # print path_info from the 2nd.
    for i in range(len(test_case["path_info"])):
        if i != 0:
            print " " * path_info_pos,
            print test_case["path_info"][i]

# def print_test_cases(test_cases):
#     for test_case in test_cases:
#         print_test_case(test_case)


do_the_test(init_test_cases_from_script())
#do_the_test(init_test_cases_from_script())
# do_the_test(init_test_cases_example2())

debuglog_file_object.close()

