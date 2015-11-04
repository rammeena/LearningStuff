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

from cinderclient import exceptions as cinder_exc

from tempest.common.utils import data_utils
from tempest import config
from tempest.openstack.common import log
from tempest.scenario import manager
from tempest import test

CONF = config.CONF

LOG = log.getLogger(__name__)


class TestVolumeBootPattern(manager.OfficialClientTest):

    """
    This test case attempts to reproduce the following steps:

     * Create in Cinder some bootable volume importing a Glance image
     * Boot an instance from the bootable volume
     * Write content to the volume
     * Delete an instance and Boot a new instance from the volume
     * Check written content in the instance
     * Create a volume snapshot while the instance is running
     * Boot an additional instance from the new snapshot based volume
     * Check written content in the instance booted from snapshot
    """
    @classmethod
    def setUpClass(cls):
        super(TestVolumeBootPattern, cls).setUpClass()

        if not CONF.volume_feature_enabled.snapshot:
            raise cls.skipException("Cinder volume snapshots are disabled")

    def _create_volume_from_image(self):
        img_uuid = CONF.compute.image_ref
        vol_name = data_utils.rand_name('volume-origin')
        return self.create_volume(name=vol_name, imageRef=img_uuid)

    def _boot_instance_from_volume(self, vol_id, keypair):
        # NOTE(gfidente): the syntax for block_device_mapping is
        # dev_name=id:type:size:delete_on_terminate
        # where type needs to be "snap" if the server is booted
        # from a snapshot, size instead can be safely left empty
        bd_map = {
            'vda': vol_id + ':::0'
        }
        security_groups = [self.security_group.name]
        create_kwargs = {
            'block_device_mapping': bd_map,
            'key_name': keypair.name,
            'security_groups': security_groups
        }
        return self.create_server(image='', create_kwargs=create_kwargs)

    def _create_snapshot_from_volume(self, vol_id):
        volume_snapshots = self.volume_client.volume_snapshots
        snap_name = data_utils.rand_name('snapshot')
        snap = volume_snapshots.create(volume_id=vol_id,
                                       force=True,
                                       display_name=snap_name)
        self.addCleanup_with_wait(self.volume_client.volume_snapshots, snap.id,
                                  exc_type=cinder_exc.NotFound)
        self.status_timeout(volume_snapshots,
                            snap.id,
                            'available')
        return snap

    def _create_volume_from_snapshot(self, snap_id):
        vol_name = data_utils.rand_name('volume')
        return self.create_volume(name=vol_name, snapshot_id=snap_id)

    def _stop_instances(self, instances):
        # NOTE(gfidente): two loops so we do not wait for the status twice
        for i in instances:
            self.compute_client.servers.stop(i)
        for i in instances:
            self.status_timeout(self.compute_client.servers,
                                i.id,
                                'SHUTOFF')

    def _detach_volumes(self, volumes):
        # NOTE(gfidente): two loops so we do not wait for the status twice
        for v in volumes:
            self.volume_client.volumes.detach(v)
        for v in volumes:
            self.status_timeout(self.volume_client.volumes,
                                v.id,
                                'available')

    def _ssh_to_server(self, server, keypair):
        if CONF.compute.use_floatingip_for_ssh:
            floating_ip = self.compute_client.floating_ips.create()
            self.addCleanup(self.delete_wrapper, floating_ip)
            server.add_floating_ip(floating_ip)
            ip = floating_ip.ip
        else:
            network_name_for_ssh = CONF.compute.network_for_ssh
            ip = server.networks[network_name_for_ssh][0]

        try:
            return self.get_remote_client(
                ip,
                private_key=keypair.private_key)
        except Exception:
            LOG.exception('ssh to server failed')
            self._log_console_output()
            raise

    def _get_content(self, ssh_client):
        return ssh_client.exec_command('cat /tmp/text')

    def _write_text(self, ssh_client):
        text = data_utils.rand_name('text-')
        ssh_client.exec_command('echo "%s" > /tmp/text; sync' % (text))

        return self._get_content(ssh_client)

    def _delete_server(self, server):
        self.compute_client.servers.delete(server)
        self.delete_timeout(self.compute_client.servers, server.id)

    def _check_content_of_written_file(self, ssh_client, expected):
        actual = self._get_content(ssh_client)
        self.assertEqual(expected, actual)

    @test.services('compute', 'volume', 'image')
    def test_volume_boot_pattern(self):
        keypair = self.create_keypair()
        self.security_group = self._create_security_group_nova()

        # create an instance from volume
        volume_origin = self._create_volume_from_image()
        instance_1st = self._boot_instance_from_volume(volume_origin.id,
                                                       keypair)

        # write content to volume on instance
        ssh_client_for_instance_1st = self._ssh_to_server(instance_1st,
                                                          keypair)
        text = self._write_text(ssh_client_for_instance_1st)

        # delete instance
        self._delete_server(instance_1st)

        # create a 2nd instance from volume
        instance_2nd = self._boot_instance_from_volume(volume_origin.id,
                                                       keypair)

        # check the content of written file
        ssh_client_for_instance_2nd = self._ssh_to_server(instance_2nd,
                                                          keypair)
        self._check_content_of_written_file(ssh_client_for_instance_2nd, text)

        # snapshot a volume
        snapshot = self._create_snapshot_from_volume(volume_origin.id)

        # create a 3rd instance from snapshot
        volume = self._create_volume_from_snapshot(snapshot.id)
        instance_from_snapshot = self._boot_instance_from_volume(volume.id,
                                                                 keypair)

        # check the content of written file
        ssh_client = self._ssh_to_server(instance_from_snapshot, keypair)
        self._check_content_of_written_file(ssh_client, text)

        # NOTE(gfidente): ensure resources are in clean state for
        # deletion operations to succeed
        self._stop_instances([instance_2nd, instance_from_snapshot])
        self._detach_volumes([volume_origin, volume])


class TestVolumeBootPatternV2(TestVolumeBootPattern):
    def _boot_instance_from_volume(self, vol_id, keypair):
        bdms = [{'uuid': vol_id, 'source_type': 'volume',
                 'destination_type': 'volume', 'boot_index': 0,
                 'delete_on_termination': False}]
        security_groups = [self.security_group.name]
        create_kwargs = {
            'block_device_mapping_v2': bdms,
            'key_name': keypair.name,
            'security_groups': security_groups
        }
        return self.create_server(image='', create_kwargs=create_kwargs)
