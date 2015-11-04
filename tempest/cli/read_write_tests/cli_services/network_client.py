import logging

from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.cli_services import base
from tempest import config
from tempest.common.utils import data_utils

CONF = config.CONF

class BaseNeutronClient(read_write_tests.ClientTestBase):
    """ Base client class for Neutron
    """

    def __init__(self):
        self.service = CONF.network.catalog_type
        self.base = base.CliClientBase()

    def create_network(self, name=None, **kwargs):
        """ create a network with specified name and optional arguments
        """

        if name is None:
            name = data_utils.rand_name("Test-Network")

        p_list = [name]
        for key, value in kwargs.iteritems():
            # todo: hack to deal if paramter name contains ':'
            if "9999" in key:
                key = str(key).replace("9999", ":")
            item = '--' + key + ' ' + value
            p_list.append(item)

        result = self.neutron('net-create', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "network")
        return dict_result

    def list_networks(self, **kwargs):
        """ list networks by optional filter arguments

        This function currently supports specifying arguments in long form
        For example --field FIELD will be specified instead of -F FIELD
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        network_list = self.neutron('net-list', params_list=p_list)
        network_list = self.base.list_table2dict(network_list, "network")
        return network_list

    def delete_network(self, network):
        """ deletes the specified network
        """

        self.neutron('net-delete', params_list=[network])

    def update_network(self, network, new_network_name):
        """ update network
        """

        self.neutron(
            'net_update',
            params_list=[network, '--name %s' % new_network_name]
        )

    def show_network(self, network):
        """ show information of a specified network
        """

        result = self.neutron('net-show', params_list=[network])
        dict_result = self.base.create_table2dict(result, "network")
        return dict_result

    def create_subnet(self, network, cidr, **kwargs):
        """ create a subnet for specified network and CIDR

        @param network: Name/ID of network under which the
                        subnet will be created
        @param cidr: CIDR of subnet to create
        """

        p_list = [network, cidr]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        result = self.neutron('subnet-create', params_list=p_list)
        subnet_result = self.base.create_table2dict(result, "subnet")
        return subnet_result

    def list_subnets(self, **kwargs):
        """ list subnets by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        subnet_list = self.neutron('subnet-list', params_list=p_list)
        subnet_list = self.base.list_table2dict(subnet_list, "subnet")
        return subnet_list

    def update_subnet(self, subnet, new_subnet_name, **kwargs):
        """ update subnet with specified name optional paramters
        """

        p_list = [subnet, '--name %s' % new_subnet_name]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        self.neutron('subnet_update', params_list=p_list)

    def delete_subnet(self, subnet):
        """ delete the specified subnet
        """

        self.neutron('subnet-delete', params_list=[subnet])

    def show_subnet(self, subnet):
        """ show information of a specified subnet
        """

        result = self.neutron('subnet-show', params_list=[subnet])
        dict_result = self.base.create_table2dict(result, "subnet")
        return dict_result

    def list_agents(self, **kwargs):
        """ list agents by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        agent_list = self.neutron('agent-list', params_list=p_list)
        agent_list = self.base.list_table2dict(agent_list, "agents")
        return agent_list

    def show_agent(self, agent):
        """ show information of a specified agent
        """

        result = self.neutron('agent-show', params_list=[agent])
        dict_result = self.base.create_table2dict(result, "agent")
        return dict_result

    def create_port(self, network, **kwargs):
        """ create a port for specified network (ID or Name)
        """

        p_list = [network]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        result = self.neutron('port-create', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "port")
        return dict_result

    def delete_port(self, port):
        """ delete a specified port
        """

        self.neutron('port-delete', params_list=[port])

    def list_ports(self, **kwargs):
        """ list subnets by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        port_list = self.neutron('port-list', params_list=p_list)
        port_list = self.base.list_table2dict(port_list, "ports")
        return port_list

    def update_port(self, port, **kwargs):
        """ update port for specified paramters
        """

        p_list = [port]
        for key, value in kwargs.iteritems():
            if "_" in key:
                key = str(key).replace("_", "-")
            item = '--' + key + ' ' + value
            p_list.append(item)

        self.neutron('port-update', params_list=p_list)

    def show_port(self, port):
        """ show information of a specified port
        """

        result = self.neutron('port-show', params_list=[port])
        dict_result = self.base.create_table2dict(result, "port")
        return dict_result

    def create_router(self, router_name=None, **kwargs):
        """ create a router with specified name and optional arguments
        """

        if router_name is None:
            router_name = data_utils.rand_name("Test-Router")

        p_list = [router_name]
        for key, value in kwargs.iteritems():
            if "_" in key:
                key = str(key).replace("_", "-")
            item = '--' + key + ' ' + str(value)
            p_list.append(item)

        result = self.neutron('router-create', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "router")
        return dict_result

    def add_interface_to_router(self, router, interface):
        """ adds an internal network interface(subnet or port) to the router

        @param router: Name/ID of router to which interface will be added
        @param interface: Name/ID of subnet or port
        """

        self.neutron('router-interface-add', params_list=[router, interface])

    def delete_interface_from_router(self, router, interface):
        """ delete the internal network interface(subnet or port)
        from the router

        @param router: Name/ID of router from which interface will be removed
        @param interface: Name/ID of subnet or port
        """

        self.neutron('router-interface-delete', params_list=[router, interface])

    def set_router_gateway(self, router, ext_interface):
        """ sets external network gateway for the router

        @param router: Name/ID of router
        @param interface: ID of the external network
        """

        self.neutron('router-gateway-set', params_list=[router, ext_interface])

    def remove_router_gateway(self, router):
        """ remove external network gateway from the router
        """

        self.neutron('router-gateway-clear', params_list=[router])

    def list_routers(self, **kwargs):
        """ list routers by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        router_list = self.neutron('router-list', params_list=p_list)
        router_list = self.base.list_table2dict(router_list, "routers")
        return router_list

    def list_router_ports(self, router, **kwargs):
        """ list router ports for given router and by optional filter arguments
        """

        p_list = [router]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        router_port_list = self.neutron('router-port-list', params_list=p_list)
        router_port_list = self.base.list_table2dict(
            router_port_list,
            "router_ports"
        )
        return router_port_list

    def delete_router(self, router):
        """ delete a specified router
        """

        self.neutron('router-delete', params_list=[router])

    def show_router(self, router):
        """ show information of a specified router
        """

        result = self.neutron('router-show', params_list=[router])
        dict_result = self.base.create_table2dict(result, "router")
        return dict_result

    def update_router(self, router, **kwargs):
        """ update router for specified paramters
        """

        p_list = [router]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        self.neutron('router-update', params_list=p_list)

    def create_security_group(self, security_group_name=None, **kwargs):
        """ create a security group with specified name and optional arguments
        """

        if security_group_name is None:
            security_group_name = data_utils.rand_name("Test-Security-Group")

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)
        p_list.append(security_group_name)

        result = self.neutron('security-group-create', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "security_group")
        return dict_result

    def add_security_group_rule(self, security_group, **kwargs):
        """ Add rule for specified security group
        """

        p_list = [security_group]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        result = self.neutron('security-group-rule-create', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "security_group_rule")
        return dict_result

    def delete_securty_group(self, security_group):
        """ delete specified security group
        """

        self.neutron('security-group-delete', params_list=[security_group])

    def delete_securty_group_rule(self, security_group_rule):
        """ delete the specified security group rule
        """

        self.neutron(
            'security-group-rule-delete',
            params_list=[security_group_rule]
        )

    def list_security_group(self, **kwargs):
        """ list security groups by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        security_group_list = self.neutron(
            'security-group-list',
            params_list=p_list
        )
        security_group_list = self.base.list_table2dict(
            security_group_list,
            "security_groups"
        )
        return security_group_list

    def list_security_group_rule(self, **kwargs):
        """ list security group rules by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        rule_list = self.neutron('security-group-rule-list', params_list=p_list)
        rule_list = self.base.list_table2dict(rule_list, "security_group_rules")
        return rule_list

    def show_security_group_rule(self, security_group_rule):
        """ show information of the specified security group rule
        """

        result = self.neutron(
            'security-group-rule-show',
            params_list=[security_group_rule]
        )
        dict_result = self.base.create_table2dict(result, "security_group_rule")
        return dict_result

    def show_security_group(self, security_group):
        """ show information of the specified security group
        """

        result = self.neutron(
            'security-group-show',
            params_list=[security_group]
        )
        dict_result = self.base.create_table2dict(result, "security_group")
        return dict_result

    def create_floating_ip(self, floating_net, **kwargs):
        """ create a floating IP from the specified network
        """

        p_list = [floating_net]
        for key, value in kwargs.iteritems():
            if "_" in key:
                key = str(key).replace("_", "-")
            item = '--' + key + ' ' + value
            p_list.append(item)

        result = self.neutron('floatingip-create', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "floating_ip")
        return dict_result

    def associate_floating_ip(self, floating_ip, port, **kwargs):
        """ create mapping between floating IP and fixed IP

        @param floating_ip: ID of floating IP to associate
        @param port: ID/name of the port to map with floating IP
        """

        p_list = [floating_ip, port]
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        result = self.neutron('floatingip-associate', params_list=p_list)
        dict_result = self.base.create_table2dict(result, "floating_ip")
        return dict_result

    def disassociate_floating_ip(self, floating_ip):
        """ remove mapping from the floating IP

        @param floating_ip: ID of floating IP to disassociate
        """

        result = self.neutron('floatingip-disassociate', params_list=[floating_ip])
        dict_result = self.base.create_table2dict(result, "floating_ip")
        return dict_result

    def delete_floating_ip(self, floating_ip):
        """ delete specified floating IP
        """

        self.neutron('floatingip-delete', params_list=[floating_ip])

    def list_floating_ip(self, **kwargs):
        """ list floating IPs by optional filter arguments
        """

        p_list = []
        for key, value in kwargs.iteritems():
            item = '--' + key + ' ' + value
            p_list.append(item)

        floating_ip_list = self.neutron('floatingip-list', params_list=p_list)
        floating_ip_list = self.base.list_table2dict(
            floating_ip_list,
            "floating_ip_list"
        )
        return floating_ip_list

    def show_floating_ip(self, floating_ip):
        """ show information of the specified floating IP
        """

        result = self.neutron('floatingip-show', params_list=[floating_ip])
        dict_result = self.base.create_table2dict(result, "floating_ip")
        return dict_result
