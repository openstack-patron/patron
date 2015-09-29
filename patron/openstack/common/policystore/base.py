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
# This is the base class for an adapter, deny all acceses.

import abc
import ast
import copy
import logging
import os
import re

from oslo_config import cfg
from oslo_serialization import jsonutils
import six

from patron.openstack.common import fileutils
from patron.openstack.common._i18n import _, _LE

policy_opts = [
    cfg.StrOpt('policy_file',
               default='policy.json',
               help=_('The JSON file that defines policies.')),
    cfg.StrOpt('policy_default_rule',
               default='default',
               help=_('Default rule. Enforced when a requested rule is not '
                      'found.')),
    cfg.MultiStrOpt('policy_dirs',
                    default=['policy.d'],
                    help=_('Directories where policy configuration files are '
                           'stored. They can be relative to any directory '
                           'in the search path defined by the config_dir '
                           'option, or absolute paths. The file defined by '
                           'policy_file must exist for these directories to '
                           'be searched.  Missing or empty directories are '
                           'ignored.')),
]

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

class BaseAdapter(object):

    # def __init__(self):
    #     self.policy_path = None

    def setDetails(self, policy_name="default-policy", type="default",
                 version="v1.0", file_name="default-policy.json", project_id = ""):
        self.loaded = False
        self.policy_name = policy_name
        self.type = type
        self.version = version
        self.file_name = file_name
        self.project_id = project_id

        self.policy_path = None
        self.use_conf = True

    def setDetails(self, policy_info, project_id = ""):
        self.loaded = False
        self.policy_name = policy_info.get("name", "default-policy")
        self.type = policy_info.get("type", "default")
        self.version = policy_info.get("version", "v1.0")
        self.file_name = policy_info.get("content", "default-policy.json")
        self.project_id = project_id

        self.policy_path = None
        self.use_conf = True

    def clear(self):
        self.loaded = False

    def load_rules(self, force_reload=False):
        """Loads policy_path's rules.

        Policy file is cached and will be reloaded if modified.

        :param force_reload: Whether to reload rules from config file.
        """

        if force_reload:
            self.use_conf = force_reload

        if self.use_conf:
            if self.file_name != "":
                if not self.policy_path:
                    self.policy_path = self._get_policy_path(self.project_id, self.file_name)

                self._load_policy_file(self.policy_path, force_reload,
                                       overwrite=False)
                # for path in CONF.policy_dirs:
                #     try:
                #         path = self._get_policy_path(path, self.project_id, self.file_name)
                #     except cfg.ConfigFilesNotFoundError:
                #         continue
                #     self._walk_through_policy_directory(path,
                #                                         self._load_policy_file,
                #                                         force_reload, False)
            else:
                LOG.info("No policy file needed for policy: %(path)s", {'path': self.policy_path})
                # LOG.info("No policy file needed for policy: (%s, %s, %s, %s, %s)" %
                #     (self.policy_name, self.type, self.version, self.file_name, self.project_id))

    @staticmethod
    def _walk_through_policy_directory(path, func, *args):
        # We do not iterate over sub-directories.
        policy_files = next(os.walk(path))[2]
        policy_files.sort()
        for policy_file in [p for p in policy_files if not p.startswith('.')]:
            func(os.path.join(path, policy_file), *args)

    def _load_policy_file(self, path, force_reload, overwrite=True):
        reloaded, data = fileutils.read_cached_file(
            path, force_reload=force_reload)
        if reloaded or not self.is_loaded() or not overwrite:
            # Edited by Yang Luo.
            self.set_policy(data, None, overwrite=overwrite, use_conf=True)
            LOG.info("Reloaded policy file: %(path)s", {'path': path})
        else:
            LOG.info("No need to reload policy file: %(path)s", {'path': path})

    def _get_policy_path(self, project_id, file_name = None):
        """Locate the policy json data file/path.

        :param path: It's value can be a full path or related path. When
                     full path specified, this function just returns the full
                     path. When related path specified, this function will
                     search configuration directories to find one that exists.

        :returns: The policy path

        :raises: ConfigFilesNotFoundError if the file/path couldn't
                 be located.
        """

        policy_path = CONF.find_file("policy.json")

        # Edited by Yang Luo.
        if project_id != "" and project_id != None and policy_path != None:
            file_path = os.path.dirname(policy_path)
            if file_name == None:
                file_name = os.path.basename(policy_path)
            custom_policy_path = file_path + "/custom_policy/" + project_id + "/" + file_name
            if os.path.exists(custom_policy_path):
                LOG.info("Custom policy path [%s] exists" % custom_policy_path)
                policy_path = custom_policy_path
            else:
                LOG.info("Custom policy path [%s] doesn't exist" % custom_policy_path)
        else:
            file_path = os.path.dirname(policy_path)
            if file_name == None:
                file_name = os.path.basename(policy_path)
            builtin_policy_path = file_path + "/" + file_name
            if os.path.exists(builtin_policy_path):
                LOG.info("Built-in policy path [%s] exists" % builtin_policy_path)
                policy_path = builtin_policy_path
            else:
                LOG.info("Built-in policy path [%s] doesn't exist" % builtin_policy_path)

        if policy_path:
            return policy_path

        raise cfg.ConfigFilesNotFoundError((path,))

    def is_loaded(self):
        return self.loaded

    def set_policy(self, data, default_rule, overwrite=True, use_conf=True):
        self.loaded = True

    def enforce(self, rule, target, creds):
        return False