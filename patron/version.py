#    Copyright 2011 OpenStack Foundation
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

import pbr.version

from patron.i18n import _LE

PATRON_VENDOR = "OpenStack Foundation"
PATRON_PRODUCT = "OpenStack Patron"
PATRON_PACKAGE = None  # OS distro package version suffix

loaded = False
version_info = pbr.version.VersionInfo('patron')
version_info.release = "2015.1.0" # added by Yang Luo.
version_info.version = "2015.1.0"
version_string = version_info.version_string


def _load_config():
    # Don't load in global context, since we can't assume
    # these modules are accessible when distutils uses
    # this module
    import ConfigParser

    from oslo_config import cfg

    import logging

    global loaded, PATRON_VENDOR, PATRON_PRODUCT, PATRON_PACKAGE
    if loaded:
        return

    loaded = True

    cfgfile = cfg.CONF.find_file("release")
    if cfgfile is None:
        return

    try:
        cfg = ConfigParser.RawConfigParser()
        cfg.read(cfgfile)

        if cfg.has_option("Patron", "vendor"):
            PATRON_VENDOR = cfg.get("Patron", "vendor")

        if cfg.has_option("Patron", "product"):
            PATRON_PRODUCT = cfg.get("Patron", "product")

        if cfg.has_option("Patron", "package"):
            PATRON_PACKAGE = cfg.get("Patron", "package")
    except Exception as ex:
        LOG = logging.getLogger(__name__)
        LOG.error(_LE("Failed to load %(cfgfile)s: %(ex)s"),
                  {'cfgfile': cfgfile, 'ex': ex})


def vendor_string():
    _load_config()

    return PATRON_VENDOR


def product_string():
    _load_config()

    return PATRON_PRODUCT


def package_string():
    _load_config()

    return PATRON_PACKAGE


def version_string_with_package():
    if package_string() is None:
        return version_info.version_string()
    else:
        return "%s-%s" % (version_info.version_string(), package_string())
