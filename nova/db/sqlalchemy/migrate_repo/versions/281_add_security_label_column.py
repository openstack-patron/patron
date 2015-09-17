# Copyright 2015 Peking University
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

# Edited by Yang Luo

from sqlalchemy import MetaData, Table, Column, Text


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)

    # Add a new column to store security label of for the object
    instances = Table('instances', meta, autoload=True)
    networks = Table('networks', meta, autoload=True)

    security_label = Column('security_label', Text, default=None)
    if not hasattr(instances.c, 'security_label'):
        instances.create_column(security_label)
    if not hasattr(networks.c, 'security_label'):
        networks.create_column(security_label.copy())


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)

    # Remove the security_label column
    instances = Table('instances', meta, autoload=True)
    networks = Table('networks', meta, autoload=True)

    if hasattr(instances.c, 'security_label'):
        instances.drop_column('security_label')
    if hasattr(networks.c, 'security_label'):
        networks.drop_column('security_label')
