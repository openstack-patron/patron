#Written by veotax.

import re
import os
import time
import subprocess
from pprint import pprint
import socket

re_run_time = re.compile('Command run time is: (.*) seconds')
re_http_error = re.compile('^ERROR(.*)\(HTTP (.*)\) \((.*)')
re_usage_error = re.compile('(.*)usage:(.*)')

######################################################################
# Explanation for "answer" field:
# Permitted:        the command is permitted by access controls
# Denied:           the command is denied by access controls, the same with HTTP 403 error
# HTTP 400 Error:   ERROR (BadRequest): Compute service of ly-compute1 is unavailable at this time. (HTTP 400)
# HTTP 409 Error:   ERROR (Conflict): Key pair 'key1' already exists. (HTTP 409)
# HTTP 412 Error:   ERROR (ClientException): Unknown Error (HTTP 412), this error is actually because path_to_op fails to find an op
# HTTP 413 Error:   ERROR (OverLimit): Over limit (HTTP 413), this error is actually because op tuple returned by path_to_op is empty
# HTTP 500 Error:   ERROR (ClientException): The server has either erred or is incapable of performing the requested operation. (HTTP 500)
# HTTP 501 Error:   ERROR (HTTPNotImplemented): Unable to get dns domain (HTTP 501)
######################################################################

if socket.gethostname() == "controller":
    macros_to_replace = {
        "$NET_ID": "net1",
        "$KEY_NAME": "key1",
        "$HOSTNAME": "ly-compute1"
    }
else: # "ly-controller"
    macros_to_replace = {
        "$NET_ID": "7416c4f4-5718-4c41-81df-b9eeb3c7ff41", # "demo-net"
        "$DEMONET_ID": "7416c4f4-5718-4c41-81df-b9eeb3c7ff41",
        "$KEY_NAME": "key1",
        "$INSTANCE_NAME": "demo-instance1",
        "$HOSTNAME": "ly-compute1",
        "$AGGRE_NAME": "aggregate1",
        "$SERVER_NAME": "",
        "$NEW_INSTANCE_NAME": "demo-instance1-new"
    }

remove_macro_pattern = ""
for k in macros_to_replace:
    remove_macro_pattern += ("\\" + k + "|")
remove_macro_pattern = remove_macro_pattern[:-1]

re_remove_macro = re.compile(remove_macro_pattern)


def macro_replace_callback(matchobj):
    if matchobj.group(0) in macros_to_replace:
        return macros_to_replace[matchobj.group(0)]
    return "!Re Replace Error!"

def get_macro_removed_command(cmd):
    return re_remove_macro.sub(macro_replace_callback, cmd)

def init_test_cases_from_script():
    file_object = open('/usr/lib/python2.7/dist-packages/patron-test/nova-cmd-test.sh', 'r')
    lines = file_object.readlines()
    file_object.close()

    test_cases = []

    cnt = 0
    for line in lines:
        if re.match("^nova", line):
            cnt = cnt + 1
            line=line.strip('\n')
            test_case = {}
            test_case["no"] = cnt
            test_case["command"] = line
            test_case["user"] = "admin"
            test_cases.append(test_case)

    return test_cases

def init_test_cases_example2():
    test_cases = []

    test_case = {}
    test_case["no"] = 1
    test_case["command"] = "nova dns-domains"
    test_case["user"] = "admin"
    test_cases.append(test_case)

    return test_cases

def init_test_cases_example():
    test_cases = []

    # Error
    test_case = {}
    test_case["no"] = 1
    test_case["command"] = "nova flavor-list"
    test_case["user"] = "admin"
    test_cases.append(test_case)

    # Permitted
    test_case = {}
    test_case["no"] = 2
    test_case["command"] = "nova list"
    test_case["user"] = "admin"
    test_cases.append(test_case)

    # Denied
    test_case = {}
    test_case["no"] = 3
    test_case["command"] = "nova service-list"
    test_case["user"] = "demo"
    test_cases.append(test_case)

    return test_cases

def do_the_test(test_cases):
    for test_case in test_cases:
        test_case["command"] = get_macro_removed_command(test_case["command"])
        mytask = subprocess.Popen("exec bash -c 'source /root/" + test_case["user"] + "-openrc.sh;" + test_case["command"] + "'", shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        response= mytask.stdout.read()

        # Uncommented it to see the real response.
        # print response

        re_res = re_run_time.search(response)
        if re_res != None:
            seconds = re_res.group(1)
        else:
            seconds = "N/A"

        re_res = re_http_error.search(response)
        if re_res != None:
            http_error = re_res.group(2)
            if http_error != "403":
                answer = "HTTP " + http_error + " Error"
            else:
                answer = "Denied"
        else:
            answer = "Permitted"

        test_case["time"] = seconds
        test_case["answer"] = answer
        print_test_case(test_case)
    return test_cases

def print_test_case(test_case):
    print('no: %-5s    cmd: %-50s    user: %-10s    answer: %-15s    time: %-10s' %
          (test_case["no"], test_case["command"], test_case["user"], test_case["answer"], test_case["time"]))

def print_test_cases(test_cases):
    for test_case in test_cases:
        print_test_case(test_case)


test_cases = do_the_test(init_test_cases_from_script())
# test_cases = do_the_test(init_test_cases_example2())


