import jsonschema

from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.neutron import utils
from rally.task import validation

"""Scenarios for Security Group page"""

@validation.add("required_services",
                services=[consts.Service.NEUTRON])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(
    context={"cleanup@openstack": ["neutron"]},
    name="NipaCloud.create_and_delete_security_group_rule",
    platform="openstack")
class CreateAndDeleteSecurityGroupRule(utils.NeutronScenario):

    def run(self, security_group_args=None,
            security_group_rule_args=None):
        """Create and delete Neutron security-group-rule.

        Measure the "neutron security-group-rule-create" and "neutron
        security-group-rule-delete" command performance.

        :param security_group_args: dict, POST /v2.0/security-groups
            request options
        :param security_group_rule_args: dict,
            POST /v2.0/security-group-rules request options
        """
        security_group_args = security_group_args or {}
        security_group_rule_args = security_group_rule_args or {}

        security_group = self._create_security_group(**security_group_args)
        msg = "security_group isn't created"
        self.assertTrue(security_group, err_msg=msg)

        security_group_rule = self._create_security_group_rule(
            security_group["security_group"]["id"], **security_group_rule_args)
        msg = "security_group_rule isn't created"
        self.assertTrue(security_group_rule, err_msg=msg)

        self._delete_security_group_rule(
            security_group_rule["security_group_rule"]["id"])
        self._delete_security_group(security_group)

@validation.add("required_services",
                services=[consts.Service.NEUTRON])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(
    context={"cleanup@openstack": ["neutron"]},
    name="NipaCloud.create_and_delete_security_group",
    platform="openstack")
class CreateAndDeleteSecurityGroup(utils.NeutronScenario):

    def run(self, security_group_create_args=None):
        """Create and delete Neutron security-groups.

        Measure the "neutron security-group-create" and "neutron
        security-group-delete" command performance.

        :param security_group_create_args: dict, POST /v2.0/security-groups
                                           request options
        """
        security_group_create_args = security_group_create_args or {}
        security_group = self._create_security_group(
            **security_group_create_args)
        self._delete_security_group(security_group)
