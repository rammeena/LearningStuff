# Copyright 2012 OpenStack Foundation
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


from tempest.api.compute import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import exceptions
from tempest import test

CONF = config.CONF


class LiveBlockMigrationNegativeTestJSON(base.BaseV2ComputeAdminTest):
    _host_key = 'OS-EXT-SRV-ATTR:host'

    @classmethod
    def setUpClass(cls):
        super(LiveBlockMigrationNegativeTestJSON, cls).setUpClass()
        if not CONF.compute_feature_enabled.live_migration:
            raise cls.skipException("Live migration is not enabled")
        cls.admin_hosts_client = cls.os_adm.hosts_client
        cls.admin_servers_client = cls.os_adm.servers_client

    def _migrate_server_to(self, server_id, dest_host):
        _resp, body = self.admin_servers_client.live_migrate_server(
            server_id, dest_host,
            CONF.compute_feature_enabled.
            block_migration_for_live_migration)
        return body

    @test.attr(type=['negative', 'gate'])
    def test_invalid_host_for_migration(self):
        # Migrating to an invalid host should not change the status
        target_host = data_utils.rand_name('host-')
        _, server = self.create_test_server(wait_until="ACTIVE")
        server_id = server['id']

        self.assertRaises(exceptions.BadRequest, self._migrate_server_to,
                          server_id, target_host)
        self.servers_client.wait_for_server_status(server_id, 'ACTIVE')


class LiveBlockMigrationNegativeTestXML(LiveBlockMigrationNegativeTestJSON):
    _host_key = (
        '{http://docs.openstack.org/compute/ext/extended_status/api/v1.1}host')
    _interface = 'xml'
