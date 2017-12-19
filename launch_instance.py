import jsonschema

from rally.common import logging
from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.plugins.openstack.wrappers import network as network_wrapper
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
from rally.task import types
from rally.task import validation

"""Scenario for Nipa.Cloud launch instance test"""

@types.convert(image={"type": "glance_image"}, flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor", image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA, consts.Service.NEUTRON])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=("network"))
@scenario.configure(context={"cleanup@openstack": ["nova", "neutron"]}, name="NipaCloud.launch_single_instance", platform="openstack")

class LaunchSingleInstance(nova_utils.NovaScenario, neutron_utils.NeutronScenario):
    def run(self, image, flavor, force_delete=False, **kwargs):
        """Boot a server with sec_group, ip, keypair and delete it.

        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        :param kwargs: Optional additional arguments for server creation
        """
        keypair = self._create_keypair()
        self.sleep_between(5, 5)
        security_group = self._create_security_group()
        self.sleep_between(5, 5)
        server = self._boot_server(image, flavor, key_name=keypair, secgroups=security_group, **kwargs)
        self.sleep_between(5, 5)
        address = network_wrapper.wrap(self.clients, self).create_floating_ip(tenant_id=server.tenant_id)
        self.sleep_between(5, 5)
        self._associate_floating_ip(server, address["ip"])
        self.sleep_between(5, 5)
        self._delete_server(server, force=force_delete)
