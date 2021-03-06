# Copyright 2012 OpenStack Foundation
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

"""Starter script for Nova Cert."""

import sys

from oslo_config import cfg
from oslo_log import log as logging

from patron import config
from patron.openstack.common.report import guru_meditation_report as gmr
from patron import service
from patron import utils
from patron import version

CONF = cfg.CONF
CONF.import_opt('cert_topic', 'patron.cert.rpcapi')


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, "patron")
    utils.monkey_patch()

    gmr.TextGuruMeditation.setup_autorun(version)

    server = service.Service.create(binary='patron-cert', topic=CONF.cert_topic)
    service.serve(server)
    service.wait()
