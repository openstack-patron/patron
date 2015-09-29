# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Peking University.
# All Rights Reserved.
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

# Edited by Yang Luo.
# This is the AND adapter, it will enforce True if and only if all sub adapters are True.

from patron.openstack.common.policystore.base import BaseAdapter

import re

class OpAndAdapter(BaseAdapter):

    def __init__(self):
        self.adapters = []

    def set_details(self, policy_info, project_id = ""):
        self.loaded = False
        self.name = policy_info.get("name")
        self.type = policy_info.get("type")
        self.version = policy_info.get("version")

        # Parse the adapter names from "content" field.
        adapter_names = re.split("[,]", policy_info.get("content", "").replace(" ", ""))
        for adapter_name in adapter_names:
            if (policy_info.has_key(adapter_name)):
                self.adapters.append(BaseAdapter.get_adapter_by_policy_info(policy_info[adapter_name], project_id))

        self.project_id = project_id

        self.policy_path = None
        self.use_conf = True

    def clear(self):
        self.loaded = False
        for adapter in self.adapters:
            adapter.clear()

    def load_rules(self, force_reload=False):
        """Loads policy_path's rules.

        Policy file is cached and will be reloaded if modified.

        :param force_reload: Whether to reload rules from config file.
        """

        if force_reload:
            self.use_conf = force_reload

        if self.use_conf:
            for adapter in self.adapters:
                adapter.load_rules(force_reload)

    def is_loaded(self):
        return True

    def enforce(self, rule, target, creds):
        for adapter in self.adapters:
            res = adapter.enforce(rule, target, creds)
            if res == False:
                return False
        return True