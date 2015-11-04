from tempest import config
from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.cli_services import network_client

CONF = config.CONF

class NeutronTestBase(read_write_tests.ClientTestBase):
    """ Base class for the Neutron tests
    """

    @classmethod
    def setUpClass(cls):
        super(NeutronTestBase, cls).setUpClass()
        if not CONF.service_available.neutron:
            raise cls.skipException("Neutron support is required")

        cls.network_client = network_client.BaseNeutronClient()
        cls.networks = []
        cls.subnets = []
        cls.routers = []
        cls.ports = []
        cls.floating_ips = []

    @classmethod
    def tearDownClass(cls):
        if CONF.service_available.neutron:
            for port in cls.ports:
                cls.network_client.delete_port(port)
            for subnet in cls.subnets:
                cls.network_client.delete_subnet(subnet)
            for network in cls.networks:
                cls.network_client.delete_network(network)
            for router in cls.routers:
                cls.network_client.delete_router(router)
            for floating_ip in cls.floating_ips:
                cls.network_client.delete_floating_ip(floating_ip)

        super(NeutronTestBase, cls).tearDownClass()

    @classmethod
    def create_network(cls, name=None, **kwargs):
        """ wrapper utility that returns a test network
        """

        network = cls.network_client.create_network(name, **kwargs)
        network_id = network["network"]["id"]
        cls.networks.append(network_id)
        return network

    @classmethod
    def create_subnet(cls, network_id, cidr):
        """ wrapper utility that returns a test subnet
        """

        subnet = cls.network_client.create_subnet(network_id, str(cidr))
        subnet_id = subnet["subnet"]["id"]
        cls.subnets.append(subnet_id)
        return subnet

    @classmethod
    def create_router(cls, name=None, **kwargs):
        """ wrapper utility that returns a test router
        """

        router = cls.network_client.create_router(name, **kwargs)
        router_id = router["router"]["id"]
        cls.routers.append(router_id)
        return router

    @classmethod
    def create_port(cls, network_id):
        """ wrapper utility that returns a test port
        """

        port = cls.network_client.create_port(network_id)
        port_id = port["port"]["id"]
        cls.ports.append(port_id)
        return port

    @classmethod
    def create_floating_ip(cls, network_id):
        """ wrapper utility that returns a test floating ip
        """

        fip = cls.network_client.create_floating_ip(network_id)
        fip_id = fip["floating_ip"]["id"]
        cls.floating_ips.append(fip_id)
        return fip_id
