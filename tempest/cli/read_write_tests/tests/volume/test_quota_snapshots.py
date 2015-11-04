import logging

from tempest import config
from tempest import exceptions
from tempest.cli.read_write_tests.tests.volume import base
from tempest.common.utils import data_utils

CONF = config.CONF
LOG = logging.getLogger(__name__)

class CinderClientSnapshotQuotaTest(base.ClientTestBase):
    """Tests for Cinder CLI client to verify snapshot
    and quota related operations.
    """

    @classmethod
    def setUpClass(cls):
        if not CONF.service_available.cinder:
            msg = ("%s skipped as Cinder is not available" % cls.__name__)
            raise cls.skipException(msg)
        super(CinderClientSnapshotQuotaTest, cls).setUpClass()

        cls.vol_name = data_utils.rand_name('Volume')
        cls.volume = cls.create_volume(name=cls.vol_name, size=4)
        cls.volume_id = cls.volume["volume"]["id"]
        cls.client.wait_for_volume_status(cls.volume_id, 'available')

        cls.snapshot_name = data_utils.rand_name('Snapshot')
        cls.snapshot = cls.create_snapshot(cls.volume_id, cls.snapshot_name)
        cls.snapshot_id = cls.snapshot["snapshot"]["id"]
        cls.client.wait_for_snapshot_status(cls.snapshot_id, status='available')

        cls.tenant_name = data_utils.rand_name('Tenant')
        cls.tenant = cls.create_tenant(cls.tenant_name)
        cls.tenant_id = cls.tenant["tenant"]["id"]

    def _verify_snapshot_created(self, snapshot_id):
        result = self.client.list_snapshots()
        snapshots = result["snapshots"]
        is_snapshot_available = len([i for i in snapshots if i['ID'] == snapshot_id and i["Status"] == 'available']) > 0
        self.assertEqual(is_snapshot_available, True)

    def test_create_snapshot(self):
        """Verifies snapshot creation"""
        snapshot_name = data_utils.rand_name('Snapshot')
        snapshot = self.client.create_snapshot(self.volume_id, snapshot_name)
        snapshot_id = snapshot["snapshot"]["id"]
        self.client.wait_for_snapshot_status(snapshot_id, 'available')
        self._verify_snapshot_created(snapshot_id)

    def test_delete_snapshot(self):
        """Verifies snapshot deletion"""
        self.client.delete_snapshot(self.snapshot_id)
        self.client.wait_for_snapshot_deletion(self.snapshot_id)
        self.assertEqual(self.client.is_snapshot_deleted(self.snapshot_id), True)

    def _is_snapshot_exist(self, snapshot_id, snapshot_name):
        result = self.client.list_snapshots()
        snapshots = result["snapshots"]
        return len([i for i in snapshots if i['ID'] == snapshot_id and i['Display Name'] == snapshot_name]) > 0

    def test_rename_snapshot(self):
        """Verifies snapshot rename operation"""
        self.assertEqual(
            self._is_snapshot_exist(
                self.snapshot_id,
                self.snapshot_name
                ),
            True
        )

        new_snapshot_name = data_utils.rand_name('Snapshot')

        self.client.rename_snapshot(self.snapshot_id, new_snapshot_name)
        self.assertEqual(
            self._is_snapshot_exist(
                self.snapshot_id,
                self.snapshot_name
                ),
            False
        )
        self.assertEqual(
            self._is_snapshot_exist(
                self.snapshot_id,
                new_snapshot_name
                ),
            True
        )

    def test_show_snapshot(self):
        """Verifies snapshot details show operation"""
        result = self.client.show_snapshot(self.snapshot_id)
        for key in ['id', 'display_name', 'volume_id']:
            self.assertEqual(result["snapshot"][key], self.snapshot["snapshot"][key])

        self.client.delete_snapshot(self.snapshot_id)
        self.client.wait_for_snapshot_deletion(self.snapshot_id)

        self.assertRaises(exceptions.CommandFailed,
            self.client.cinder,
            'snapshot-show',
            params_list=[self.snapshot_id]
        )

    def _is_tenant_exist(self, tenant_id):
        result = self.keystone_client.list_tenants()
        tenant_list = result["tenants"]
        return len([i for i in tenant_list if i['id'] == tenant_id]) > 0

    def test_show_quota(self):
        """Verifies quota show operation for volumes parameter"""

    def test_update_show_quota(self):
        """Verifies quota update operation for volumes parameter"""
        self.assertEqual(self._is_tenant_exist(self.tenant_id), True)
        self.client.show_default_quota(self.tenant_id)
        self.client.update_quota(self.tenant_id, volumes=20, gigabytes=1200, snapshots=20)
        result_after_update = self.client.show_quota(self.tenant_id)

        self.assertEqual(result_after_update["tenant"]["volumes"], 20)
        self.assertEqual(result_after_update["tenant"]["gigabytes"], 1200)
        self.assertEqual(result_after_update["tenant"]["snapshots"], 20)
