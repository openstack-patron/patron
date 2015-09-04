#    Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# NOTE(comstud): You may scratch your head as you see code that imports
# this module and then accesses attributes for objects such as Instance,
# etc, yet you do not see these attributes in here. Never fear, there is
# a little bit of magic. When objects are registered, an attribute is set
# on this module automatically, pointing to the newest/latest version of
# the object.


def register_all():
    # NOTE(danms): You must make sure your object gets imported in this
    # function in order for it to be registered by services that may
    # need to receive it via RPC.
    __import__('patron.objects.agent')
    __import__('patron.objects.aggregate')
    __import__('patron.objects.bandwidth_usage')
    __import__('patron.objects.block_device')
    __import__('patron.objects.cell_mapping')
    __import__('patron.objects.compute_node')
    __import__('patron.objects.dns_domain')
    __import__('patron.objects.ec2')
    __import__('patron.objects.external_event')
    __import__('patron.objects.fixed_ip')
    __import__('patron.objects.flavor')
    __import__('patron.objects.floating_ip')
    __import__('patron.objects.hv_spec')
    __import__('patron.objects.instance')
    __import__('patron.objects.instance_action')
    __import__('patron.objects.instance_fault')
    __import__('patron.objects.instance_group')
    __import__('patron.objects.instance_info_cache')
    __import__('patron.objects.instance_mapping')
    __import__('patron.objects.instance_numa_topology')
    __import__('patron.objects.instance_pci_requests')
    __import__('patron.objects.keypair')
    __import__('patron.objects.migration')
    __import__('patron.objects.network')
    __import__('patron.objects.network_request')
    __import__('patron.objects.numa')
    __import__('patron.objects.pci_device')
    __import__('patron.objects.pci_device_pool')
    __import__('patron.objects.tag')
    __import__('patron.objects.quotas')
    __import__('patron.objects.security_group')
    __import__('patron.objects.security_group_rule')
    __import__('patron.objects.service')
    __import__('patron.objects.vcpu_model')
    __import__('patron.objects.virt_cpu_topology')
    __import__('patron.objects.virtual_interface')
