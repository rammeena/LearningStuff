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

from tempest.services.baremetal import base


class BaremetalClientV1(base.BaremetalClient):
    """
    Base Tempest REST client for Ironic API v1.

    Specific implementations must implement serialize and deserialize
    methods in order to send requests to Ironic.

    """
    def __init__(self, auth_provider):
        super(BaremetalClientV1, self).__init__(auth_provider)
        self.version = '1'
        self.uri_prefix = 'v%s' % self.version

    @base.handle_errors
    def list_nodes(self):
        """List all existing nodes."""
        return self._list_request('nodes')

    @base.handle_errors
    def list_chassis(self):
        """List all existing chassis."""
        return self._list_request('chassis')

    @base.handle_errors
    def list_ports(self, **kwargs):
        """List all existing ports."""
        return self._list_request('ports', **kwargs)

    @base.handle_errors
    def list_nodestates(self, uuid):
        """List all existing states."""
        return self._list_request('/nodes/%s/states' % uuid)

    @base.handle_errors
    def list_ports_detail(self, **kwargs):
        """Details list all existing ports."""
        return self._list_request('/ports/detail', **kwargs)

    @base.handle_errors
    def list_drivers(self):
        """List all existing drivers."""
        return self._list_request('drivers')

    @base.handle_errors
    def show_node(self, uuid):
        """
        Gets a specific node.

        :param uuid: Unique identifier of the node in UUID format.
        :return: Serialized node as a dictionary.

        """
        return self._show_request('nodes', uuid)

    @base.handle_errors
    def show_chassis(self, uuid):
        """
        Gets a specific chassis.

        :param uuid: Unique identifier of the chassis in UUID format.
        :return: Serialized chassis as a dictionary.

        """
        return self._show_request('chassis', uuid)

    @base.handle_errors
    def show_port(self, uuid):
        """
        Gets a specific port.

        :param uuid: Unique identifier of the port in UUID format.
        :return: Serialized port as a dictionary.

        """
        return self._show_request('ports', uuid)

    def show_driver(self, driver_name):
        """
        Gets a specific driver.

        :param driver_name: Name of driver.
        :return: Serialized driver as a dictionary.
        """
        return self._show_request('drivers', driver_name)

    @base.handle_errors
    def create_node(self, chassis_id, **kwargs):
        """
        Create a baremetal node with the specified parameters.

        :param cpu_arch: CPU architecture of the node. Default: x86_64.
        :param cpu_num: Number of CPUs. Default: 8.
        :param storage: Disk size. Default: 1024.
        :param memory: Available RAM. Default: 4096.
        :param driver: Driver name. Default: "fake"
        :return: A tuple with the server response and the created node.

        """
        node = {'chassis_uuid': chassis_id,
                'properties': {'cpu_arch': kwargs.get('cpu_arch', 'x86_64'),
                               'cpu_num': kwargs.get('cpu_num', 8),
                               'storage': kwargs.get('storage', 1024),
                               'memory': kwargs.get('memory', 4096)},
                'driver': kwargs.get('driver', 'fake')}

        return self._create_request('nodes', 'node', node)

    @base.handle_errors
    def create_chassis(self, **kwargs):
        """
        Create a chassis with the specified parameters.

        :param description: The description of the chassis.
            Default: test-chassis
        :return: A tuple with the server response and the created chassis.

        """
        chassis = {'description': kwargs.get('description', 'test-chassis')}

        return self._create_request('chassis', 'chassis', chassis)

    @base.handle_errors
    def create_port(self, node_id, **kwargs):
        """
        Create a port with the specified parameters.

        :param node_id: The ID of the node which owns the port.
        :param address: MAC address of the port.
        :param extra: Meta data of the port. Default: {'foo': 'bar'}.
        :param uuid: UUID of the port.
        :return: A tuple with the server response and the created port.

        """
        port = {'extra': kwargs.get('extra', {'foo': 'bar'}),
                'uuid': kwargs['uuid']}

        if node_id is not None:
            port['node_uuid'] = node_id

        if kwargs['address'] is not None:
            port['address'] = kwargs['address']

        return self._create_request('ports', 'port', port)

    @base.handle_errors
    def delete_node(self, uuid):
        """
        Deletes a node having the specified UUID.

        :param uuid: The unique identifier of the node.
        :return: A tuple with the server response and the response body.

        """
        return self._delete_request('nodes', uuid)

    @base.handle_errors
    def delete_chassis(self, uuid):
        """
        Deletes a chassis having the specified UUID.

        :param uuid: The unique identifier of the chassis.
        :return: A tuple with the server response and the response body.

        """
        return self._delete_request('chassis', uuid)

    @base.handle_errors
    def delete_port(self, uuid):
        """
        Deletes a port having the specified UUID.

        :param uuid: The unique identifier of the port.
        :return: A tuple with the server response and the response body.

        """
        return self._delete_request('ports', uuid)

    @base.handle_errors
    def update_node(self, uuid, **kwargs):
        """
        Update the specified node.

        :param uuid: The unique identifier of the node.
        :return: A tuple with the server response and the updated node.

        """
        node_attributes = ('properties/cpu_arch',
                           'properties/cpu_num',
                           'properties/storage',
                           'properties/memory',
                           'driver')

        patch = self._make_patch(node_attributes, **kwargs)

        return self._patch_request('nodes', uuid, patch)

    @base.handle_errors
    def update_chassis(self, uuid, **kwargs):
        """
        Update the specified chassis.

        :param uuid: The unique identifier of the chassis.
        :return: A tuple with the server response and the updated chassis.

        """
        chassis_attributes = ('description',)
        patch = self._make_patch(chassis_attributes, **kwargs)

        return self._patch_request('chassis', uuid, patch)

    @base.handle_errors
    def update_port(self, uuid, patch):
        """
        Update the specified port.

        :param uuid: The unique identifier of the port.
        :param patch: List of dicts representing json patches.
        :return: A tuple with the server response and the updated port.

        """

        return self._patch_request('ports', uuid, patch)

    @base.handle_errors
    def set_node_power_state(self, node_uuid, state):
        """
        Set power state of the specified node.

        :param node_uuid: The unique identifier of the node.
        :state: desired state to set (on/off/reboot).

        """
        target = {'target': state}
        return self._put_request('nodes/%s/states/power' % node_uuid,
                                 target)

    @base.handle_errors
    def validate_driver_interface(self, node_uuid):
        """
        Get all driver interfaces of a specific node.

        :param uuid: Unique identifier of the node in UUID format.

        """

        uri = '{pref}/{res}/{uuid}/{postf}'.format(pref=self.uri_prefix,
                                                   res='nodes',
                                                   uuid=node_uuid,
                                                   postf='validate')

        return self._show_request('nodes', node_uuid, uri=uri)
