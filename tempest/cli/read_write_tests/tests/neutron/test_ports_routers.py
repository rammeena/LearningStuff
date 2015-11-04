import netaddr

from tempest import test
from tempest import config
from tempest.common.utils import data_utils
from tempest.cli.read_write_tests.tests.neutron import base

CONF = config.CONF

class NeutronClientPortRouterFirewallTest(base.NeutronTestBase):
    """ Test the operations for ports, routers and firewalls
    """

    @classmethod
    def setUpClass(cls):
        if not test.is_extension_enabled('router', 'network'):
            msg = "router extension not enabled."
            raise cls.skipException(msg)
        super(NeutronClientPortRouterFirewallTest, cls).setUpClass()

        cidr = str(netaddr.IPNetwork(CONF.network.tenant_network_cidr))

        cls.network = cls.create_network()
        cls.network_id = cls.network["network"]["id"]

        cls.subnet = cls.create_subnet(cls.network_id, cidr=cidr)
        cls.subnet_id = cls.subnet["subnet"]["id"]

        cls.port = cls.create_port(cls.network_id)
        cls.port_id = cls.port["port"]["id"]

        cls.router = cls.create_router()
        cls.router_id = cls.router["router"]["id"]

    def _delete_port(self, port_id):
        self.network_client.delete_port(port_id)
        result = self.network_client.list_ports()
        ports_list = result["ports"]
        found = any([i for i in ports_list if i["id"] == port_id])
        self.assertFalse(found)

    def _delete_router(self, router_id):
        self.network_client.delete_router(router_id)
        result = self.network_client.list_routers()
        router_list = result["routers"]
        found = any([i for i in router_list if i["id"] == router_id])
        self.assertFalse(found)

    def _create_security_group(self):
        result = self.network_client.create_security_group()
        security_group_id = result["security_group"]["id"]

        # Allow security group rule for ping
        self.network_client.add_security_group_rule(
            security_group=security_group_id,
            protocol="icmp",
            direction="ingress"
        )
        self.addCleanup(self._delete_security_group, security_group_id)
        return security_group_id

    def _delete_security_group(self, security_group_id):
        self.network_client.delete_securty_group(security_group_id)
        result = self.network_client.list_security_group()
        sec_group_list = result["security_groups"]
        found = any([i for i in sec_group_list if i["id"] == security_group_id])
        self.assertFalse(found)

    def test_create_update_delete_port(self):
        # Verify port creation
        sec_group_id = self._create_security_group()
        result = self.network_client.create_port(self.network_id)
        port = result["port"]

        # Schedule port deletion with verification upon test completion
        self.addCleanup(self._delete_port, port["id"])

        # Verify created port exists in ports list
        result = self.network_client.list_ports()
        ports_list = result["ports"]
        found = any([i for i in ports_list if i["id"] == port["id"]])
        self.assertTrue(found)

        # Verify port update with security group
        self.network_client.update_port(
            port["id"],
            security_group=sec_group_id
        )
        result_update = self.network_client.show_port(port["id"])
        updated_port = result_update["port"]
        self.assertEqual(updated_port["security_groups"], sec_group_id)

    def test_show_port(self):
        # Verify the details of port
        result = self.network_client.show_port(self.port_id)
        port = result["port"]
        self.assertEqual(port["id"], self.port_id)
        self.assertEqual(
            self.port["port"]["admin_state_up"],
            port["admin_state_up"]
        )
        self.assertEqual(self.port["port"]["device_id"], port["device_id"])
        self.assertEqual(
            self.port["port"]["device_owner"],
            port["device_owner"]
        )
        self.assertEqual(self.port["port"]["mac_address"], port["mac_address"])
        self.assertEqual(self.port["port"]["name"], port["name"])
        self.assertEqual(
            self.port["port"]["security_groups"],
            port["security_groups"]
        )
        self.assertEqual(self.port["port"]["network_id"], port["network_id"])

    def test_agent_list_show(self):
        # list agents
        result = self.network_client.list_agents()
        agents = result["agents"]

        # get first agent for which admin state is up
        agent_id = [i["id"] for i in agents if i["admin_state_up"] == "True"][0]
        result = self.network_client.show_agent(agent_id)
        agent_info = result["agent"]
        self.assertEqual(agent_info["admin_state_up"], "True")

    def test_create_show_list_update_delete_router(self):
        # Create a router
        name = data_utils.rand_name("test-router-")
        result = self.network_client.create_router(
            router_name=name,
            admin_state_up=False
        )
        router_id = result["router"]["id"]
        self.addCleanup(self._delete_router, router_id)

        self.assertEqual(result["router"]["name"], name)
        self.assertEqual(result["router"]["admin_state_up"], "False")

        # Show details of the created router
        show_result = self.network_client.show_router(router_id)
        self.assertEqual(show_result["router"]["name"], name)
        self.assertEqual(show_result["router"]["admin_state_up"], "False")

        # List routers and verify if created router is there in the list
        list_result = self.network_client.list_routers()
        routers_list = list()
        for router in list_result["routers"]:
            routers_list.append(router["id"])
        self.assertIn(router_id, routers_list)

        # Update the name of router and verify if it is updated
        updated_name = 'updated-' + name
        self.network_client.update_router(router_id, name=updated_name)
        show_result = self.network_client.show_router(router_id)
        self.assertEqual(show_result["router"]["name"], updated_name)
