# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 OpenStack Foundation.
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

"""
Common Policy Engine Implementation

Policies can be expressed in one of two forms: A list of lists, or a
string written in the new policy language.

In the list-of-lists representation, each check inside the innermost
list is combined as with an "and" conjunction--for that check to pass,
all the specified checks must pass.  These innermost lists are then
combined as with an "or" conjunction. As an example, take the following
rule, expressed in the list-of-lists representation::

    [["role:admin"], ["project_id:%(project_id)s", "role:projectadmin"]]

This is the original way of expressing policies, but there now exists a
new way: the policy language.

In the policy language, each check is specified the same way as in the
list-of-lists representation: a simple "a:b" pair that is matched to
the correct class to perform that check::

 +===========================================================================+
 |            TYPE                |                SYNTAX                    |
 +===========================================================================+
 |User's Role                     |              role:admin                  |
 +---------------------------------------------------------------------------+
 |Rules already defined on policy |          rule:admin_required             |
 +---------------------------------------------------------------------------+
 |Against URL's¹                  |         http://my-url.org/check          |
 +---------------------------------------------------------------------------+
 |User attributes²                |    project_id:%(target.project.id)s      |
 +---------------------------------------------------------------------------+
 |Strings                         |        <variable>:'xpto2035abc'          |
 |                                |         'myproject':<variable>           |
 +---------------------------------------------------------------------------+
 |                                |         project_id:xpto2035abc           |
 |Literals                        |         domain_id:20                     |
 |                                |         True:%(user.enabled)s            |
 +===========================================================================+

¹URL checking must return 'True' to be valid
²User attributes (obtained through the token): user_id, domain_id or project_id

Conjunction operators are available, allowing for more expressiveness
in crafting policies. So, in the policy language, the previous check in
list-of-lists becomes::

    role:admin or (project_id:%(project_id)s and role:projectadmin)

The policy language also has the "not" operator, allowing a richer
policy rule::

    project_id:%(project_id)s and not role:dunce

Attributes sent along with API calls can be used by the policy engine
(on the right side of the expression), by using the following syntax::

    <some_value>:%(user.id)s

Contextual attributes of objects identified by their IDs are loaded
from the database. They are also available to the policy engine and
can be checked through the `target` keyword::

    <some_value>:%(target.role.name)s

Finally, two special policy checks should be mentioned; the policy
check "@" will always accept an access, and the policy check "!" will
always reject an access.  (Note that if a rule is either the empty
list ("[]") or the empty string, this is equivalent to the "@" policy
check.)  Of these, the "!" policy check is probably the most useful,
as it allows particular rules to be explicitly disabled.
"""

import abc
import ast
import copy
import logging
import os
import re

from oslo_config import cfg
from oslo_serialization import jsonutils
import six
import six.moves.urllib.parse as urlparse
import six.moves.urllib.request as urlrequest

from patron.openstack.common import fileutils
from patron.openstack.common._i18n import _, _LE

from patron.openstack.common.policystore import default


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
CONF.register_opts(policy_opts)

LOG = logging.getLogger(__name__)

_checks = {}


def list_opts():
    """Entry point for oslo-config-generator."""
    return [(None, copy.deepcopy(policy_opts))]


class PolicyNotAuthorized(Exception):

    def __init__(self, rule):
        msg = _("Policy doesn't allow %s to be performed.") % rule
        super(PolicyNotAuthorized, self).__init__(msg)



class Enforcer(object):
    """Responsible for loading and enforcing rules.

    :param policy_file: Custom policy file to use, if none is
                        specified, `CONF.policy_file` will be
                        used.
    :param rules: Default dictionary / Rules to use. It will be
                  considered just in the first instantiation. If
                  `load_rules(True)`, `clear()` or `set_rules(True)`
                  is called this will be overwritten.
    :param default_rule: Default rule to use, CONF.default_rule will
                         be used if none is specified.
    :param use_conf: Whether to load rules from cache or config file.
    :param overwrite: Whether to overwrite existing rules when reload rules
                      from config file.
    """

    def __init__(self, policy_file=None, rules=None,
                 default_rule=None, use_conf=True, overwrite=True):
        # Edited by Yang Luo.
        # self.default_rule = default_rule or CONF.policy_default_rule
        # self.rules = Rules(rules, self.default_rule)
        self.default_enforcer = default.DefaultEnforcer(rules, default_rule, use_conf, overwrite)
        self.current_enforcer = self.default_enforcer

        self.metadata_path = None
        self.policy_path = None
        self.policy_file = policy_file or CONF.policy_file
        self.use_conf = use_conf
        self.overwrite = overwrite

        self.current_policy = {}

    def clear(self):
        """Clears Enforcer rules, policy's cache and policy's path."""

        # self.set_rules({})
        self.current_enforcer.clear()

        fileutils.delete_cached_file(self.metadata_path)
        fileutils.delete_cached_file(self.policy_path)

        # self.default_rule = None
        self.current_enforcer.default_rule = None

        self.metadata_path = None
        self.policy_path = None

    def load_rules(self, project_id, force_reload=False):
        """Loads policy_path's rules.

        Policy file is cached and will be reloaded if modified.

        :param force_reload: Whether to reload rules from config file.
        """

        if force_reload:
            self.use_conf = force_reload

        if self.use_conf:
            if not self.metadata_path:
                self.metadata_path = self._get_metadata_path(self.policy_file, project_id)

            if self.metadata_path:
                self._load_metadata_file(self.metadata_path, force_reload,
                                   overwrite=self.overwrite)
                current_policy_file = self.current_policy['name'] + ".json"
                current_policy_type = self.current_policy['type']
                LOG.info("current_policy_file = %s, current_policy_type = %s" % (current_policy_file, current_policy_type))
            else:
                current_policy_file = None
                current_policy_type = None
                LOG.info("current_policy_file = %s, current_policy_type = %s" % (current_policy_file, current_policy_type))
                LOG.info("Metadata file not found, disable the multi-policy feature.")
                project_id = None

            if not self.policy_path:
                self.policy_path = self._get_policy_path(self.policy_file, project_id, current_policy_file)

            self._load_policy_file(self.policy_path, force_reload,
                                   overwrite=self.overwrite)
            for path in CONF.policy_dirs:
                try:
                    path = self._get_policy_path(path, project_id, current_policy_file)
                except cfg.ConfigFilesNotFoundError:
                    continue
                self._walk_through_policy_directory(path,
                                                    self._load_policy_file,
                                                    force_reload, False)

    @staticmethod
    def _walk_through_policy_directory(path, func, *args):
        # We do not iterate over sub-directories.
        policy_files = next(os.walk(path))[2]
        policy_files.sort()
        for policy_file in [p for p in policy_files if not p.startswith('.')]:
            func(os.path.join(path, policy_file), *args)

    def _load_metadata_file(self, path, force_reload, overwrite=True):
            reloaded, data = fileutils.read_cached_file(
                path, force_reload=force_reload)
            if reloaded or not self.current_enforcer.is_loaded() or not overwrite:
                json_metadata = jsonutils.loads(data)
                LOG.debug("Reloaded metadata file: %(path)s",
                          {'path': path})
                self.current_policy['name'] = json_metadata['current-policy']
                self.current_policy['type'] = json_metadata[json_metadata['current-policy']]['type']

    def _load_policy_file(self, path, force_reload, overwrite=True):
            reloaded, data = fileutils.read_cached_file(
                path, force_reload=force_reload)
            if reloaded or not self.current_enforcer.is_loaded() or not overwrite:
                # Edited by Yang Luo.
                self.current_enforcer.set_policy(data, None, overwrite=overwrite, use_conf=True)
                LOG.debug("Reloaded policy file: %(path)s",
                          {'path': path})

    def _fixpath(p):
        """Apply tilde expansion and absolutization to a path."""
        return os.path.abspath(os.path.expanduser(p))

    def _get_metadata_path(self, path, project_id, file_name = "metadata.json"):
        """Locate the metadata json data file/path.

        :param path: It's value can be a full path or related path. When
                     full path specified, this function just returns the full
                     path. When related path specified, this function will
                     search configuration directories to find one that exists.

        :returns: The metadata path
        """
        policy_path = CONF.find_file(path)

        # Edited by Yang Luo.
        if project_id != "" and project_id != None and policy_path != None:
            file_path = os.path.dirname(policy_path)
            if file_name == None:
                file_name = os.path.basename(policy_path)
            custom_policy_path = file_path + "/custom_policy/" + project_id + "/" + file_name
            if os.path.exists(custom_policy_path):
                LOG.info("Custom metadata path [%s] exists" % custom_policy_path)
                return custom_policy_path
            else:
                LOG.info("Custom metadata path [%s] doesn't exist" % custom_policy_path)
                return None

    def _get_policy_path(self, path, project_id, file_name = None):
        """Locate the policy json data file/path.

        :param path: It's value can be a full path or related path. When
                     full path specified, this function just returns the full
                     path. When related path specified, this function will
                     search configuration directories to find one that exists.

        :returns: The policy path

        :raises: ConfigFilesNotFoundError if the file/path couldn't
                 be located.
        """
        policy_path = CONF.find_file(path)

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

        if policy_path:
            return policy_path

        raise cfg.ConfigFilesNotFoundError((path,))

    def enforce(self, rule, target, creds, do_raise=False,
                exc=None, *args, **kwargs):
        """Checks authorization of a rule against the target and credentials.

        :param rule: A string or BaseCheck instance specifying the rule
                    to evaluate.
        :param target: As much information about the object being operated
                    on as possible, as a dictionary.
        :param creds: As much information about the user performing the
                    action as possible, as a dictionary.
        :param do_raise: Whether to raise an exception or not if check
                        fails.
        :param exc: Class of the exception to raise if the check fails.
                    Any remaining arguments passed to enforce() (both
                    positional and keyword arguments) will be passed to
                    the exception class. If not specified, PolicyNotAuthorized
                    will be used.

        :return: Returns False if the policy does not allow the action and
                exc is not provided; otherwise, returns a value that
                evaluates to True.  Note: for rules using the "case"
                expression, this True value will be the specified string
                from the expression.
        """

        self.load_rules(creds['project_id'])

        # Edited by Yang Luo.
        result = self.current_enforcer.enforce(rule, target, creds)

        # If it is False, raise the exception if requested
        if do_raise and not result:
            if exc:
                raise exc(*args, **kwargs)

            raise PolicyNotAuthorized(rule)

        return result

