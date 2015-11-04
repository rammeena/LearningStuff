from tempest.cli import read_write_tests
from tempest import config

from tempest.cli.read_write_tests.cli_services import volumes_client, keystone_client

CONF = config.CONF

class ClientTestBase(read_write_tests.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()
        cls.client = cls.volume_client = volumes_client.BaseVolumesClient()
        cls.volumes = []
        cls.snapshots = []
        cls.keystone_client = keystone_client.BaseKeystoneClient()
        cls.tenants = []

    @classmethod
    def tearDownClass(cls):
        for volume in cls.volumes:
            cls.volume_client.delete_volume(volume)
            cls.volume_client.wait_for_volume_deletion(volume_id=volume)

        for snapshot in cls.snapshots:
            cls.volume_client.delete_snapshot(snapshot)
            cls.volume_client.wait_for_snapshot_deletion(snapshot_id=snapshot)
            
        for tenant in cls.tenants:
            cls.keystone_client.delete_tenant(tenant)

        super(ClientTestBase, cls).tearDownClass()

    @classmethod
    def create_volume(cls, name="default_volume", size=1):
        cls.result = cls.volume_client.create_volume(name, size)
        volume_id = cls.result["volume"]["id"]
        cls.volumes.append(volume_id)
        return cls.result

    @classmethod
    def create_snapshot(cls, volume_id, name=None):
        cls.result = cls.volume_client.create_snapshot(volume_id, name)
        snapshot_id = cls.result["snapshot"]["id"]
        cls.snapshots.append(snapshot_id)
        return cls.result

    @classmethod
    def create_tenant(cls, name=None):
        cls.result = cls.keystone_client.create_tenant(name)
        tenant_id = cls.result["tenant"]["id"]
        cls.tenants.append(tenant_id)
        return cls.result
