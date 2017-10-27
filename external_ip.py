import jsonschema

from rally.common import logging
from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.plugins.openstack.wrappers import network as network_wrapper
from rally.task import validation
from rally.task import types

LOG = logging.getLogger(__name__)

"""Scenarios for External IP page"""

@validation.add("required_services",
                services=[consts.Service.NEUTRON])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("external_network_exists", param_name="floating_network")
@scenario.configure(context={"cleanup@openstack": ["neutron"]},
                    name="NipaCloud.create_and_delete_floating_ip",
                    platform="openstack")
class CreateAndDeleteFloatingIP(neutron_utils.NeutronScenario):

    def run(self, floating_network=None, floating_ip_args=None):
        """Create and delete floating IPs.

        Measure the "neutron floating-ip-create" and "neutron
        floating-ip-delete" commands performance.

        :param floating_network: str, external network for floating IP creation
        :param floating_ip_args: dict, POST /floatingips request options
        """
        floating_ip_args = floating_ip_args or {}
        floating_ip = self._create_floatingip(floating_network,
                                              **floating_ip_args)
        self._delete_floating_ip(floating_ip["floatingip"])

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("required_contexts", contexts=("network"))
@scenario.configure(
    context={"cleanup@openstack": ["nova", "neutron.floatingip"]},
    name="NipaCloud.boot_associate_dissociate_floating_ip_and_delete",
    platform="openstack")
class BootAssociateDissociateFloatingIPAndDelete(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Boot a server associate and dissociate a floating IP from it.

        The scenario first boot a server and create a floating IP. then
        associate the floating IP to the server.Finally dissociate the floating
        IP.

        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param kwargs: Optional additional arguments for server creation
        """
        server = self._boot_server(image, flavor)
        address = network_wrapper.wrap(self.clients, self).create_floating_ip(
            tenant_id=server.tenant_id)
        self._associate_floating_ip(server, address["ip"])
        self._dissociate_floating_ip(server, address["ip"])
        self._delete_server(server, force=force_delete)