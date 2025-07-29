#!/usr/bin/env python3
# coding: utf-8
# Copyright 2024 Huawei Technologies Co., Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ===========================================================================
import os
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import common_info, common_utils


class DockerRuntimeInstaller:
    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                resources_dir=dict(type="str", required=True),
            )
        )
        self.resources_dir = os.path.expanduser(self.module.params["resources_dir"])
        self.messages = []

    def install_pkg(self):
        arch = common_info.ARCH
        arch_pattern = arch
        if arch == "x86_64":
            arch_pattern = "x86?64"    # old package mix x86-64 and x86_64
        run_files, messages = common_utils.find_files(os.path.join(self.resources_dir, "mindxdl/dlPackage/{}".format(arch)),
                                                      "Ascend-docker-runtime*{}.run".format(arch_pattern))
        self.messages.extend(messages)
        if not run_files:
            self.messages.append("docker-runtime file not found, exiting...")
            return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)
        run_file = run_files[0]
        try:
            _, messages = common_utils.run_command(self.module, "bash {} --help".format(run_file))
            cmd_arg = ""
            if any("nox11" in message for message in messages):
                cmd_arg = " --nox11"
            _, messages = common_utils.run_command(self.module, "bash {} --uninstall{}".format(run_file, cmd_arg))
            self.messages.extend(messages)
            _, messages = common_utils.run_command(self.module, "bash {} --install{}".format(run_file, cmd_arg))
            self.messages.extend(messages)
            _, messages = common_utils.run_command(self.module, "systemctl daemon-reload")
            self.messages.extend(messages)
            _, messages = common_utils.run_command(self.module, "systemctl restart docker")
            self.messages.extend(messages)
            # retry 10 times, wait 30s every time for k8s recovery from docker restart
            for _ in range(10):
                try:
                    _, _ = common_utils.run_command(self.module, "kubectl get nodes")
                except Exception as err:
                    self.messages.append(str(err))
                    self.messages.append("k8s not ok, retry...")
                    time.sleep(30)
            return self.module.exit_json(msg="\n".join(self.messages), rc=0, changed=True)
        except Exception as e:
            self.messages.append(str(e))
            return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=True)


def main():
    installer = DockerRuntimeInstaller()
    installer.install_pkg()


if __name__ == "__main__":
    main()
