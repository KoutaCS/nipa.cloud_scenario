import jsonschema

from rally.common import logging
from rally import consts
from rally.plugins import scenario 
from rally.plugins.openstack.nova import utils as nova_utils
from rally.plugins.openstack.wrappers import network as network_wrapper
from rally.task import types
from rally.task import validation

"""step
    1. mutilple instance
    2. image
    3. flavor
    4. security group
    5. keypair
    6. floating IP"""

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=(consts.Service.NOVA))
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=("network"))
@scenario.configure(context={"cleanup@openstack": ["nova", "neutron.floatingip"]},
                    name="NipaCloud.launch_single_instance", platform="openstack")
class LaunchSingleInstance(nova_utils.NovaScenario):
    def run(self, image, flavor, force_delete=False):
        keypair = self._create_keypair()
        server = self._boot_server(image, flavor, key_name=keypair)
        security_group = self._create_security_group()
        self._add_server_secgroups(server, security_group)
        address = network_wrapper.wrap(self.clients, self).create_floating_ip(
            tenant_id=server.tenant_id)
        self._associate_floating_ip(server, address["ip"])
        self._delete_server(server, force=force_delete)