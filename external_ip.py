from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.neutron import utils
from rally.task import validation


"""Scenarios for External IP"""

@validation.add("required_services",
                services=[consts.Service.NEUTRON])
@validation.add("required_platform", platform="openstack", users=True)
@validation.add("external_network_exists", param_name="floating_network")
@scenario.configure(context={"cleanup@openstack": ["neutron"]},
                    name="NeutronNetworks.create_and_delete_floating_ips",
                    platform="openstack")
class CreateAndDeleteFloatingIps(utils.NeutronScenario):

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
        self._delete_floating_ip(floating_ip["floatingip"]

@validation.add("")