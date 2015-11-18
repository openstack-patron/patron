
import os
import api_paste_change.apc as apc
import shutil
import tempest_integration_test as tepit
import time

services = ["nova", "glance", "neutron", "cinder", "heat", "ceilometer"]
service_map = {
    "nova": "compute",
    "glance": "image",
    "neutron": "network",
    "cinder": "volume",
    "heat": "orchestration",
    "ceilometer": "telemetry",
}

def reset_all_services():
    for single_service in services:
        apc.toggle_aem(single_service, False)
        apc.toggle_aem2(single_service, False)

def restart_all_services():
    for single_service in services:
        apc.restart_service(single_service)


def clear_tempest_log():
    f = open("/var/log/tempest/tempest.log", "w+")
    f.truncate()
    f.close()

# clear /var/log/tempest before running tests
def clear_before_test(service_name):
    path = "/var/log/tempest/" + service_name + "/"
    if os.path.exists(path):
        os.popen("rm -r " + path)

# main action
def do_test(times, service, AEMenabled, cacheEnabled):
    reset_all_services()
    base_dir = "/var/log/tempest/" + service + "/"
    if not os.path.exists(base_dir):
        os.popen("mkdir " + base_dir)

    apc.toggle_aem(service, True)
    apc.toggle_aem2(service, True)

    if AEMenabled:
        apc.toggle_aem_variable("aem", True)
        if cacheEnabled:
            flag = "aem_on_cache_on"
            apc.toggle_aem_variable("cache", True)
        else:
            flag = "aem_on_cache_off"
            apc.toggle_aem_variable("cache", False)
    else:
        flag = "aem_off"
        apc.toggle_aem_variable("aem", False)

    file_dir = base_dir + flag + "/"
    if not os.path.exists(file_dir):
        os.popen("mkdir " + file_dir)

    for i in range(times):
        restart_all_services()
        clear_tempest_log()
        print ("The %dth time, running %s test==>>>>>>>>>" % (i+1, service.upper()))
        cmd = "nosetests /usr/lib/python2.7/dist-packages/tempest/api/" + service_map[service] \
              + "/ 1> /var/log/tempest/tempest_result.log 2> /var/log/tempest/tempest_result.log"
        os.popen(cmd)

        result = os.popen("tail -3 /var/log/tempest/tempest_result.log")
        result_str = result.read()
        if result_str == '':
            result_str = "Nosetests Error!"
        result_str = result_str.replace("\n\n", "\n")

        f = open(file_dir + "result.log", "a+")
        f.write("##################################################################\nNo. %d, %s, %s\n\n" % (i+1, service, flag))
        f.write(result_str)
        f.close()

        ultimate_f = open("/var/log/tempest/ultimate_result.log", "a+")
        ultimate_f.write("##################################################################\nNo. %d, %s, %s\n\n" % (i+1, service, flag))
        ultimate_f.write(result_str)
        ultimate_f.close()

        tepit.core_parse()
        old_op_path = "/var/log/tempest/" + service + "-op.log"
        result1 = os.popen("tail -3 " + old_op_path)
        result1_str = result1.read()
        if result1_str == "":
            result1_str = "Parse Error!"

        # print result1.read()
        f1 = open(file_dir + "result.log", "a+")
        f1.write("\n------------------------------------------------------------------\n")
        f1.write("%s\n\n" % result1_str)
        f1.close()

        ultimate_f1 = open("/var/log/tempest/ultimate_result.log", "a+")
        ultimate_f1.write("\n------------------------------------------------------------------\n")
        ultimate_f1.write("%s\n\n" % result1_str)
        ultimate_f1.close()

        old_tempest_log_path = "/var/log/tempest/tempest.log"
        new_op_path = file_dir + str(i+1) + "-op.log"
        new_tempest_log_path = file_dir + str(i+1) + "-tempest.log"
        # for backup
        shutil.copyfile(old_op_path, new_op_path)
        shutil.copyfile(old_tempest_log_path, new_tempest_log_path)
        print "Run successfully!\n"
        time.sleep(3)

# do test loop
times = 0
for service in services:
    clear_before_test(service)
    do_test(times, service, False, False)
    do_test(times, service, True, False)
    do_test(times, service, True, True)


# do single test
service_name = "cinder"
clear_before_test(service_name)
do_test(2, service_name, False, False)
do_test(2, service_name, True, False)
do_test(2, service_name, True, True)