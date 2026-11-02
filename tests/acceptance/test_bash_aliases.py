"""Owned Bash aliases load in interactive Bash and preserve unowned file data."""

import json
import re
import shlex

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")


def user_ride(vm, *args, check=True):
    command = [f"{vm.repo}/ride.sh", *args]
    return vm.run("sudo -u ride-test bash -lc " + shlex.quote(shlex.join(command)), check=check)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_bash_aliases_interactive_lifecycle_and_user_content(vm):
    vm.run("sudo dnf -y install eza", timeout=900)
    rc = "/home/ride-test/.bashrc"
    aliases = "/home/ride-test/.bash_aliases"
    vm.run(f"printf '%s\\n' '# user rc before' 'export USER_RC=1' > {rc}")
    vm.run(f"printf '%s\\n' '# user aliases before' \"alias ll='ls -la'\" > {aliases}")
    profile = vm.put_json("shell-aliases", {
        "schemaVersion": 1,
        "id": "shell-aliases-fixture",
        "description": "Opt-in user alias acceptance profile",
        "operations": [{
            "id": "setting.bash-aliases",
            "state": "configured",
            "value": json.dumps(["ls-eza", "wanip", "wanip4", "wanip6"], separators=(",", ":")),
        }],
    })
    plan = user_ride(vm, "plan", "--profile", profile)
    assert "setting.bash-aliases" in plan.stdout and "candidate" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", profile, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = user_ride(vm, "apply", "--profile", profile, "--allow-candidate")
    match = RUN_ID.search(applied.stdout)
    assert match, applied.stdout
    journal = json.loads(vm.run(
        f"cat /home/ride-test/.local/state/ride-fedora/runs/{match.group(1)}.json"
    ).stdout)
    assert journal["steps"][0]["selectedValue"] == '["ls-eza","wanip","wanip4","wanip6"]'
    owner = "/home/ride-test/.local/state/ride-fedora/owned/setting.bash-aliases.json"
    vm.run(f"test \"$(stat -c %a {owner})\" = 600")
    visible = vm.run(
        "sudo -u ride-test bash -lc " + shlex.quote(
            "bash --noprofile --rcfile /home/ride-test/.bashrc -ic "
            + shlex.quote("alias ls; alias wanip; alias wanip4; alias wanip6")
        ),
    ).stdout
    assert "alias ls='eza'" in visible
    assert "https://api64.ipify.org" in visible
    assert "https://api.ipify.org" in visible
    assert "https://api6.ipify.org" in visible
    eza = vm.run(
        "sudo -u ride-test bash -lc " + shlex.quote(
            "bash --noprofile --rcfile /home/ride-test/.bashrc -ic 'ls --version'"
        ),
    )
    assert "eza" in eza.stdout.lower()
    assert "configured" in user_ride(vm, "status", "setting.bash-aliases").stdout
    repeat = user_ride(vm, "apply", "--profile", profile, "--allow-candidate")
    assert "unchanged setting.bash-aliases" in repeat.stdout

    vm.run(f"printf '%s\\n' '# later user rc edit' >> {rc}")
    vm.run(f"printf '%s\\n' '# later user alias edit' >> {aliases}")
    user_ride(vm, "remove", "--profile", profile, "--allow-candidate")
    final_rc = vm.run(f"cat {rc}").stdout
    final_aliases = vm.run(f"cat {aliases}").stdout
    assert "export USER_RC=1" in final_rc and "later user rc edit" in final_rc
    assert "alias ll='ls -la'" in final_aliases and "later user alias edit" in final_aliases
    assert "RIDE managed Bash aliases" not in final_rc
    assert "RIDE managed Bash aliases" not in final_aliases
    vm.run(f"test ! -e {owner}")
