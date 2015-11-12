import re
import pprint
from patron.aem import patron_verify as patron
import os
op_map = {}


def parse_five_keys(test):
    key_calls = patron.PatronVerify.key_calls

    # test = "req_port = 8774, req_api_version = u'/v2', req_method = 'POST', req_path_info = u'/df1d1e97c4f54e5a8d790d4684c3fa2a/servers/detail', req_inner_action = u''"
    # test = "req_port = 9696, req_api_version = u'/v2.0', req_method = 'DELETE', req_path_info = u'/ports/d6853199-69c7-4699-9173-e6f0d257c172', req_inner_action = u'', op=$ 'delete_port'"
    five_key_pattern = re.compile(
        "req_port = u?(.*), req_api_version = u?(.*), req_method = u?'(.*)', req_path_info = u?'(.*)', req_inner_action = u?'(.*)',")

    match = re.match(five_key_pattern, test)
    if match != None:
        port = match.group(1)
        version = match.group(2)
        version = version.strip("'")
        method = match.group(3)
        path_info = match.group(4)
        inner_action = match.group(5)

        str_path_info = patron.PatronVerify.get_template_path_info(path_info, key_calls)
        str_inner_action = patron.PatronVerify.get_templated_inner_action(path_info, inner_action)
        if str_path_info != "/":
            five_key_tuple = (int(port), version, str_path_info, method, str_inner_action)
            return five_key_tuple
        else:
            return ()
    else:
        return ()


# parse op
def op_parse(string):
    op_pattern = re.compile("^'(.*)\'\n20", re.S)
    m = re.match(op_pattern, string)
    if m != None:
        return m.group(1)


# runtime result
def rs_parse(string):
    # print string
    rs = []
    rs_pattern = re.compile(".*Response - Headers: {.*'status': '([0-9]{3})',", re.S)
    rs_pattern2 = re.compile(".*Response Status: ([0-9]{3})", re.S)

    time_pattern = re.compile(".* ([0-9]{1}.[0-9]{3}s)\n", re.S)
    m = re.match(rs_pattern, string)
    m1 = re.match(time_pattern, string)
    # print m.group(1)
    if m != None:
        rs.append(m.group(1))
    else:
        m = re.match(rs_pattern2, string)
        if m != None:
            rs.append(m.group(1))
        else:
            rs.append("NoneCode")
    if m1 != None:
        rs.append(m1.group(1))
    else:
        rs.append('0s')
    return rs


def do_clear(service):
    if service == '':
        return
    else:
        f = open('/var/log/tempest/'+ service + '-op.log', 'w+')
    f.truncate()
    f.close

# write results in file in line
def do_write(num, five_key_tuple, result, time, service):
    if service == '':
        return
    else:
        f = open('/var/log/tempest/'+ service + '-op.log', 'a+')
    f.write("%-8r  |   %-90r  |   %-30r  |   %-10r\n" % (num, five_key_tuple, result, time))
    f.close


def do_write_time(total, len, service):
    if service == '':
        return
    else:
        f = open('/var/log/tempest/'+ service + '-op.log', 'a+')
    f.write("\n\n----------------------------------------------------------------------------------------"
            "---------------------------------------------------------\n\n")
    f.write("Total time : %.3fs\nCommand number : %d\nAverage time per command : %.3fs" % (total, len, total / len))
    f.write("\n\n----------------------------------------------------------------------------------------"
            "---------------------------------------------------------\n\n")
    f.close()

def do_write_op_map(a, service):
    if service == '':
        return
    else:
        f = open('/var/log/tempest/'+ service + '-op.log', 'a+')
        f.write(a)
        f.close()


# core parser
def core_parse():
    t = ''
    total = 0
    result0 = ''
    service = ''
    f = open('/var/log/tempest/tempest.log')
    STRING = f.read()
    lists = STRING.split("### ")

    for i in range(1, len(lists)):
        five_key_tuple = ()
        # print lists[i]
        ops = []
        if lists[i].find("$ ") != -1:
            # five keys
            test = lists[i].split("$ ")[0]

            five_key_tuple = parse_five_keys(test)
            # op
            tmp = lists[i].split("$ ")
            l = len(tmp)

            if l > 2:
                for j in range(1, l - 1):
                    tmp[j] = tmp[j].strip()
                    tmp[j] = tmp[j].strip("\n")
                    tmp[j] = tmp[j].strip("'")
                    if tmp[j] != None:
                        ops.append(tmp[j])
            tmp[-1] = tmp[-1].strip()
            last_op = op_parse(tmp[-1])
            if last_op != None:
                ops.append(last_op)
            ops_tuple = tuple(ops)

            if service == '':
                if 8774 in five_key_tuple:
                    service = 'nova'
                elif 9292 in five_key_tuple:
                    service = 'glance'
                elif 9696 in five_key_tuple:
                    service = 'neutron'
                do_clear(service)

            # print ops_tuple
            # runtime result
            result = rs_parse(tmp[-1])
            if len(result) > 1:
                t = result[1]
                each_time = result[1][0:len(result[1]) - 1]
                each_time = float(each_time)
                total = total + each_time
            if len(result) > 0:
                if result[0] == '200' or result[0] == '204' or result[0] == '202' or result[0] == '201':
                    result0 = "Permited"
                elif result[0] == '403':
                    result0 = 'Denied'
                else:
                    result0 = "HttpCode : " + result[0]
            do_write(i, five_key_tuple, result0, t, service)
            if five_key_tuple!=():
                op_map[five_key_tuple] = ops_tuple

        elif lists[i].find("op=") != -1:
            # five keys
            test = lists[i].split("op=")[0]

            five_key_tuple = parse_five_keys(test)

            if service == '':
                if 8774 in five_key_tuple:
                    service = 'nova'
                elif 9292 in five_key_tuple:
                    service = 'glance'
                elif 9696 in five_key_tuple:
                    service = 'neutron'
                do_clear(service)

            # op
            ops_tuple1 = ()
            # runtime result
            tmp = lists[i].split("op=")[1]
            result = rs_parse(tmp)
            if len(result) > 1:
                t = result[1]
                each_time = result[1][0:len(result[1]) - 1]
                each_time = float(each_time)
                total = total + each_time
            if len(result) > 0:
                if result[0] == '200' or result[0] == '204' or result[0] == '202' or result[0] == '201':
                    result0 = "Permited"
                elif result[0] == '403':
                    result0 = 'Denied'
                else:
                    result0 = "HttpCode : " + result[0]
            do_write(i, five_key_tuple, result0, t, service)
            if five_key_tuple!=():
                op_map[five_key_tuple] = ops_tuple1

    do_write_time(total, len(lists) - 1, service)
    op_map_str = pprint.pformat(op_map)
    do_write_op_map(op_map_str, service)

    print total


core_parse()
