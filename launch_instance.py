import jsonschema

from rally.common import logging
from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.plugins.openstack.wrappers import network as network_wrapper
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
from rally.plugins.openstack.scenarios.vm import utils as vm_utils
from rally.task import types
from rally.common import validation
from rally.task import atomic
from rally.plugin.common import validators

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image", fail_on_404_image=False)
@validation.add("valid_command", param_name="command")
@validation.add("number", param_name="port", minval=1, maxval=65535,
                nullable=True, integer_only=True)
@validation.add("external_network_exists", param_name="floating_network")
@validation.add("required_services", services=[consts.Service.NOVA,
                                               consts.Service.NEUTRON])
@validation.add("required_param_or_context",
                param_name="image", ctx_name="image_command_customizer")
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova", "neutron"],
                             "keypair@openstack": {},
                             "allow_ssh@openstack": None},
                    name="NipaCloud.launch_single_instance",
                    platform="openstack")
class LaunchSingleInstance(vm_utils.VMScenario, neutron_utils.NeutronScenario):

    def run(self, flavor, username, password=None,
            image,
            command=None, floating_network=None, port=22,
            use_floating_ip=True, force_delete=False, wait_for_ping=True,
            max_log_length=None):
        
        security_group = self._create_security_group()
        server, fip = self._boot_server_with_fip(
            image, flavor, use_floating_ip=use_floating_ip,
            floating_network=floating_network,
            key_name=self.context["user"]["keypair"]["name"],
            , secgroups=security_group)
        try:
            if wait_for_ping:
                self._wait_for_ping(fip["ip"])

            code, out, err = self._run_command(
                fip["ip"], port, username, password, command=command)
            text_area_output = ["StdErr: %s" % (err or "(none)"),
                                "StdOut:"]
            if code:
                raise exceptions.ScriptError(
                    "Error running command %(command)s. "
                    "Error %(code)s: %(error)s" % {
                        "command": command, "code": code, "error": err})
            # Let's try to load output data
            try:
                data = json.loads(out)
                # 'echo 42' produces very json-compatible result
                #  - check it here
                if not isinstance(data, dict):
                    raise ValueError
            except ValueError:
                # It's not a JSON, probably it's 'script_inline' result
                data = []
        except (exceptions.TimeoutException,
                exceptions.SSHTimeout):
            console_logs = self._get_server_console_output(server,
                                                           max_log_length)
            LOG.debug("VM console logs:\n%s" % console_logs)
            raise

        finally:
            self._delete_server_with_fip(server, fip,
                                         force_delete=force_delete)

        if isinstance(data, dict) and set(data) == {"additive", "complete"}:
            for chart_type, charts in data.items():
                for chart in charts:
                    self.add_output(**{chart_type: chart})
        else:
            # it's a dict with several unknown lines
            text_area_output.extend(out.split("\n"))
            self.add_output(complete={"title": "Script Output",
                                      "chart_plugin": "TextArea",
                                      "data": text_area_output})
