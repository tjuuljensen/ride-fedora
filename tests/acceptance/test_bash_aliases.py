"""Owned Bash aliases load in interactive Bash and preserve unowned file data."""

import json
import re
import shlex
from pathlib import Path

import pytest


RUN_ID = re.compile(r"Run ID: ([0-9]{8}T[0-9]{6}Z-[0-9]+-[0-9]+)")
ROOT = Path(__file__).resolve().parents[2]


def user_ride(vm, *args, catalog=None, check=True):
    command = [f"{vm.repo}/ride.sh", *args]
    env = ""
    if catalog:
        env = "RIDE_CATALOG_PATH=" + shlex.quote(catalog) + " "
    return vm.run("sudo -u ride-test env " + env + "bash -lc " + shlex.quote(shlex.join(command)), check=check)


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_bash_aliases_interactive_lifecycle_and_user_content(vm):
    catalog_data = json.loads((ROOT / "catalog/operations.json").read_text(encoding="utf-8"))
    operation = next(item for item in catalog_data["operations"] if item["id"] == "setting.bash-aliases")
    operation["unsetState"] = "absent"
    catalog = vm.put_json("bash-aliases-acceptance-catalog", catalog_data)
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
    plan = user_ride(vm, "plan", "--profile", profile, catalog=catalog)
    assert "setting.bash-aliases" in plan.stdout and "candidate" in plan.stdout
    refused = user_ride(vm, "apply", "--profile", profile, catalog=catalog, check=False)
    assert refused.returncode != 0 and "--allow-candidate" in refused.stderr
    applied = user_ride(vm, "apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    match = RUN_ID.search(applied.stdout)
    assert match, applied.stdout
    apply_run_id = match.group(1)
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
    assert "configured" in user_ride(vm, "status", "setting.bash-aliases", catalog=catalog).stdout
    repeat = user_ride(vm, "apply", "--profile", profile, "--allow-candidate", catalog=catalog)
    assert "unchanged setting.bash-aliases" in repeat.stdout

    vm.run(f"printf '%s\\n' '# later user rc edit' >> {rc}")
    vm.run(f"printf '%s\\n' '# later user alias edit' >> {aliases}")
    unset = user_ride(vm, "unset", "setting.bash-aliases", "--allow-candidate", catalog=catalog)
    unset_run_id = RUN_ID.search(unset.stdout).group(1)
    assert "absent" in user_ride(vm, "status", "setting.bash-aliases", catalog=catalog).stdout
    assert "RIDE managed Bash aliases" not in vm.run(f"cat {rc} {aliases}").stdout
    repeated_unset = user_ride(vm, "unset", "setting.bash-aliases", "--allow-candidate", catalog=catalog)
    assert "unchanged setting.bash-aliases" in repeated_unset.stdout
    user_ride(vm, "restore", "--run-id", unset_run_id, "--allow-candidate", catalog=catalog)
    assert "configured" in user_ride(vm, "status", "setting.bash-aliases", catalog=catalog).stdout
    assert "alias ls='eza'" in vm.run(f"cat {aliases}").stdout
    assert "RIDE managed Bash aliases" in vm.run(f"cat {rc} {aliases}").stdout
    user_ride(vm, "restore", "--run-id", apply_run_id, "--allow-candidate", catalog=catalog)
    assert "absent" in user_ride(vm, "status", "setting.bash-aliases", catalog=catalog).stdout
    final_rc = vm.run(f"cat {rc}").stdout
    final_aliases = vm.run(f"cat {aliases}").stdout
    assert "export USER_RC=1" in final_rc and "later user rc edit" in final_rc
    assert "alias ll='ls -la'" in final_aliases and "later user alias edit" in final_aliases
    assert "RIDE managed Bash aliases" not in final_rc
    assert "RIDE managed Bash aliases" not in final_aliases
    vm.run(f"test ! -e {owner}")
