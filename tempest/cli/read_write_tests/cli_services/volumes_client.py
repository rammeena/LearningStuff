import logging

from tempest import exceptions
from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.cli_services import base
from tempest.cli.read_write_tests.common import common_alg
from tempest import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

class BaseVolumesClient(read_write_tests.ClientTestBase):
    """
    Base client class
    """
    def __init__(self):
        self.service = CONF.volume.catalog_type
        self.build_interval = CONF.volume.build_interval
        self.build_timeout = CONF.volume.build_timeout
        self.base = base.CliClientBase()

    def list_volumes(self):
        """List all the volumes created."""
        volume_list = self.cinder('list')
        volume_list = self.base.list_table2dict(volume_list, "volumes")
        return volume_list

    def get_volume(self, volume_id):
        """Returns the details of a single volume."""
        result = self.cinder('show', params_list=[volume_id])
        volume = self.base.create_table2dict(result, "volume")
        return volume

    def show_quota(self, tenant_id):
        """Returns the quota details of specified tenant"""
        result = self.cinder('quota-show', params_list=[tenant_id])
        quota = self.base.create_table2dict(result, "quota")
        return quota

    def show_default_quota(self, tenant_id):
        """Returns the default quota for specified tenant"""
        result = self.cinder('quota-defaults', params_list=[tenant_id])
        quota = self.base.create_table2dict(result, "quota")
        return quota

    def update_quota(self, tenant_id, **kwargs):
        """Updates quota parameters for specified tenant"""
        params_list = []
        for k, v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            params_list.append(item)
        params_list.append(tenant_id)
        self.cinder('quota-update', params_list=params_list)

    def create_volume(self, name=None, size=None):
        """Creates a new Volume
        @param name: Name of the volume
        @param size: Size of volume in GB
        """
        if size is None:
            size = CONF.volume.volume_size
        if name:
            result = self.cinder('create', params_list=['--display-name %s' % name, size])
        else:
            result = self.cinder('create', params_list=[size])
        result = self.base.create_table2dict(result, "volume")
        return result

    def rename_volume(self, volume_id, new_name):
        """Updates (rename) the Specified Volume."""
        self.cinder('rename', params_list=[volume_id, new_name])

    def create_snapshot(self, volume_id, name=None):
        """Creates the snapshot of Specified Volume"""
        if name:
            result = self.cinder(
                'snapshot-create',
                params_list=['--display-name %s' % name, volume_id]
            )
        else:
            result = self.cinder('snapshot-create', params_list=[volume_id])
        snapshot = self.base.create_table2dict(result, "snapshot")
        return snapshot

    def show_snapshot(self, snapshot_id):
        """Returns the details of specified snapshot"""
        result = self.cinder('snapshot-show', params_list=[snapshot_id])
        snapshot = self.base.create_table2dict(result, "snapshot")
        return snapshot

    def list_snapshots(self):
        """List all snapshots."""
        result = self.cinder('snapshot-list')
        snapshot_list = self.base.list_table2dict(result, "snapshots")
        return snapshot_list

    def delete_snapshot(self, snapshot_id):
        self.cinder('snapshot-delete', params_list=[snapshot_id])

    def rename_snapshot(self, snapshot_id, new_name):
        """Updates (renames) the specified snapshot"""
        self.cinder('snapshot-rename', params_list=[snapshot_id, new_name])

    def volume_type_list(self):
        """List volume type."""
        result = self.cinder('type-list')
        types = self.base.list_table2dict(result, "volumes")
        return types

    def volume_extra_specs_list(self):
        """List volume extra specs."""
        result = self.cinder('extra-specs-list')
        extra_specs = self.base.list_table2dict(result, "volumes")
        return extra_specs

    def verify_volume_status(self, volume_id, status):
        """Returns True if current status of volume is same as specified status
        """
        body = self.get_volume(volume_id)
        current_status = body["volume"]["status"]
        if current_status == 'error':
            raise exceptions.VolumeBuildErrorException(volume_id=volume_id)
        return current_status == status

    def verify_snapshot_status(self, snapshot_id, status):
        """Returns True if current status of snapshot is same as specified status
        """
        body = self.show_snapshot(snapshot_id)
        current_status = body["snapshot"]["status"]
        if current_status == 'error':
            raise exceptions.SnapshotBuildErrorException(snapshot_id=snapshot_id)
        return current_status == status

    def wait_for_volume_status(self, volume_id, status):
        """Waits for a Volume to reach a given status."""

        message = 'Volume %s failed to reach %s status within '\
                  'the required time (%s seconds).' % (volume_id,
                                                       status,
                                                       self.build_timeout)
        common_alg.wait_and_throw_on_timeout(
            lambda: self.verify_volume_status(volume_id, status),
            self.build_interval,
            self.build_timeout,
            message
        )

    def wait_for_snapshot_status(self, snapshot_id, status):
        """Waits for a Snapshot to reach a given status."""
        message = 'Snapshot %s failed to reach %s status within '\
                  'the required time (%s seconds).' % (snapshot_id,
                                                       status,
                                                       self.build_timeout)
        common_alg.wait_and_throw_on_timeout(
            lambda: self.verify_snapshot_status(snapshot_id, status),
            self.build_interval,
            self.build_timeout,
            message
        )

    def is_volume_deleted(self, volume_id):
        if self.verify_volume_status(volume_id, 'error_deleting'):
            raise exceptions.TempestException("Unknown error deleting volume. Check logs...")
        result = self.list_volumes()
        volumes = result["volumes"]
        return len([i for i in volumes if i['ID'] == volume_id]) == 0

    def is_snapshot_deleted(self, snapshot_id):
        if self.verify_snapshot_status(snapshot_id, 'error_deleting'):
            raise exceptions.TempestException("Unknown error deleting snapshot. Check logs...")
        result = self.list_snapshots()
        snapshots = result["snapshots"]
        return len([i for i in snapshots if i['ID'] == snapshot_id]) == 0

    def wait_for_volume_deletion(self, volume_id):
        """Waits for the specified volume to be deleted"""
        message = 'Volume %s failed to be deleted within '\
                  'required time (%s seconds)' % (volume_id,
                                                  self.build_timeout)
        common_alg.wait_and_throw_on_timeout(
            lambda: self.is_volume_deleted(volume_id),
            self.build_interval,
            self.build_timeout,
            message
        )

    def wait_for_snapshot_deletion(self, snapshot_id):
        """Waits for the specified snapshot to be deleted"""
        message = 'Snapshot %s failed to be deleted within '\
                  'required time (%s seconds)' % (snapshot_id,
                                                  self.build_timeout)
        common_alg.wait_and_throw_on_timeout(
            lambda: self.is_snapshot_deleted(snapshot_id),
            self.build_interval,
            self.build_timeout,
            message
        )

    def delete_volume(self, volume_id):
        self.cinder('delete', params_list=[volume_id])

