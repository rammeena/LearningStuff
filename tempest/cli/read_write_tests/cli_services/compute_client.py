import logging
import re
import testtools
import time
import os

from tempest import cli
from tempest import exceptions
from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.cli_services import base
from tempest import config
from tempest.common.utils import data_utils

CONF = config.CONF
LOG = logging.getLogger(__name__)

class BaseComputeClient(read_write_tests.ClientTestBase):
    """
    Base client class
    """
    def __init__(self):
        self.service = CONF.compute.catalog_type
        self.build_interval = CONF.compute.build_interval
        self.build_timeout = CONF.compute.build_timeout
        self.base = base.CliClientBase()

    def delete_server(self, server_id):
        self.nova('delete', params_list=[server_id])

    def list_servers(self, **kwargs):
        """List all the created servers."""
        p_list = []
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        server_list = self.nova('list', params_list=p_list)
        server_list = self.base.list_table2dict(server_list, "servers")
        return server_list

    def list_servers_minimal(self):
        result = self.nova('list', params_list=['--minimal'])
        server_list = self.base.list_table2dict(result, "servers")
        return server_list

    def get_server(self, server_id):
        """Returns the details of a single server."""
        server = self.nova('show', params_list=[server_id])
        server = self.base.create_table2dict(server, "server")
        return server

    def rename_server(self, server_id, new_name):
        """Chane the name of the given server."""
        if new_name is None:
            new_name = data_utils.rand_name("New-Server") 
        self.nova('rename', params_list=[server_id, new_name])

    def create_server(self, name=None, flavor=None, image=None, **kwargs):
        """
        Creates a new Server.

        @param name: Name of the server
        @param flavor: Id of the flavor to be used     
        @param image: Id of Image to boot the server 
        """
        if name is None:
            name = data_utils.rand_name("Test-Server") 
        if flavor is None:
            flavor = CONF.compute.flavor_ref
        if image is None:
            image = CONF.compute.image_ref
        p_list = []
        flavor = "--flavor %s" % flavor
        image = "--image %s" % image
        p_list.append(flavor)
        p_list.append(image)
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        p_list.append(name)
        result = self.nova('boot', params_list=p_list)
        result = self.base.create_table2dict(result, "server")
        return result

    def server_meta_set(self, server_id, **kwargs):
        """Set metadata for a given Server."""
        p_list = []
        p_list.append(server_id) 
        p_list.append("set")
        for k,v in kwargs.iteritems():
            item = k + '=' + v
            p_list.append(item)
        self.nova('meta', params_list=p_list)

    def server_meta_delete(self, server_id, key):
        """Delete set metadata for a given Server."""
        p_list = []
        p_list.append(server_id)
        p_list.append("delete")
        p_list.append(key)
        self.nova('meta', params_list=p_list)

    def wait_for_server_status(self, server_id, status, ready_wait=True,
                               extra_timeout=0, raise_on_error=True):

        def _get_task_state(body):
            if self.service == CONF.compute.catalog_v3_type:
                task_state = body.get("os-extended-status:task_state", None)
            else:
                task_state = body.get('OS-EXT-STS:task_state', None)
            return task_state

        body = self.get_server(server_id)
        old_status = server_status = body["server"]["status"]
        old_task_state = task_state = _get_task_state(body)
        start_time = int(time.time())
        timeout = self.build_timeout + extra_timeout
        while True:
            if status == 'BUILD' and server_status != 'UNKNOWN':
                return
            if server_status == status:
                if ready_wait:
                    if status == 'BUILD':
                        return
                    if str(task_state) == "None":
                        time.sleep(CONF.compute.ready_wait)
                        return
                else:
                    return

            time.sleep(self.build_interval)
            body = self.get_server(server_id)
            server_status = body["server"]["status"]
            task_state = _get_task_state(body)
            if (server_status != old_status) or (task_state != old_task_state):
                LOG.info('State transition "%s" ==> "%s" after %d second wait',
                         '/'.join((old_status, str(old_task_state))),
                         '/'.join((server_status, str(task_state))),
                         time.time() - start_time)
            if (server_status == 'ERROR') and raise_on_error:
                if 'fault' in body:
                    raise exceptions.BuildErrorException(body['fault'],
                                                         server_id=server_id)
                else:
                    raise exceptions.BuildErrorException(server_id=server_id)

            timed_out = int(time.time()) - start_time >= timeout

            if timed_out:
                expected_task_state = 'None' if ready_wait else 'n/a'
                message = ('Server %(server_id)s failed to reach %(status)s '
                           'status and task state "%(expected_task_state)s" '
                           'within the required time (%(timeout)s s).' %
                           {'server_id': server_id,
                            'status': status,
                            'expected_task_state': expected_task_state,
                            'timeout': timeout})
                message += ' Current status: %s.' % server_status
                message += ' Current task state: %s.' % task_state
                caller = misc_utils.find_test_caller()
                if caller:
                    message = '(%s) %s' % (caller, message)
                raise exceptions.TimeoutException(message)
            old_status = server_status
            old_task_state = task_state

    def wait_for_server_termination(self, server_id, ignore_error=False):
        """Waits for server to reach termination."""
        start_time = int(time.time())
        while True:
            try:
                body = self.get_server(server_id)
            except Exception:
                return

            server_status = body["server"]['status']
            if server_status == 'ERROR' and not ignore_error:
                raise exceptions.BuildErrorException(server_id=server_id)

            if int(time.time()) - start_time >= self.build_timeout:
                raise exceptions.TimeoutException

            time.sleep(self.build_interval)


    def is_resource_deleted(self, resource_id):
        try:
            self.get_server(resource_id)
        except Exception:
            return True
        return False

    def wait_for_resource_deletion(self, resource_id):
        """Waits for a resource to be deleted."""
        start_time = int(time.time())
        while True:
            if self.is_resource_deleted(resource_id):
                return
            if int(time.time()) - start_time >= self.build_timeout:
                raise exceptions.TimeoutException
            time.sleep(self.build_interval)
    def volume_update(self, server_id, attachment_id, volume_id):
        """Update the volume attachment"""
        attachment_id = ''
        volume_id = ''
        self.nova('volume-update', params_list=[server_id, attachment_id, volume_id])

