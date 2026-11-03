"""Probe Mozilla's documented system-wide XPI deployment paths."""

import json
from pathlib import Path
import shlex

import pytest


ADDON_ID = "uBlock0@raymondhill.net"
APP_ID = "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"


@pytest.mark.vm_target("fedora-44-workstation-x86_64")
def test_firefox_global_xpi_install_and_removal_probe(vm):
    vm.run("rpm -q firefox && firefox --version")
    vm.run("test ! -e /etc/firefox/policies/policies.json")
    vm.run("mkdir -p /home/ride-test/.mozilla/firefox/probe-global "
           "/home/ride-test/.mozilla/firefox/probe-distribution && "
           "printf '%s\\n' '[Profile0]' 'Name=global' 'IsRelative=1' "
           "'Path=probe-global' 'Default=1' > "
           "/home/ride-test/.mozilla/firefox/profiles.ini && "
           "printf 'preserve\\n' > /home/ride-test/.mozilla/firefox/"
           "probe-global/user-data.txt")
    vm.run(
        "python3 - <<'PY'\n"
        "import hashlib,json,urllib.request,zipfile,tempfile,pathlib\n"
        f"addon_id={ADDON_ID!r}; slug='ublock-origin'\n"
        "req=urllib.request.Request('https://addons.mozilla.org/api/v5/addons/addon/' + slug + '/', headers={'User-Agent':'RIDE-Firefox-deployment-probe/1'})\n"
        "with urllib.request.urlopen(req,timeout=45) as r: meta=json.load(r)\n"
        "assert meta['guid']==addon_id and meta['status']=='public'\n"
        "xpi_url='https://addons.mozilla.org/firefox/downloads/latest/' + slug + '/latest.xpi'\n"
        "req=urllib.request.Request(xpi_url,headers={'User-Agent':'RIDE-Firefox-deployment-probe/1'})\n"
        "with urllib.request.urlopen(req,timeout=60) as r: data=r.read(100*1024*1024+1)\n"
        "assert len(data)<=100*1024*1024\n"
        "expected=meta['current_version']['file']['hash'].removeprefix('sha256:')\n"
        "assert hashlib.sha256(data).hexdigest()==expected\n"
        "with tempfile.NamedTemporaryFile(suffix='.xpi') as f:\n"
        " f.write(data); f.flush()\n"
        " with zipfile.ZipFile(f.name) as z: addon=json.loads(z.read('manifest.json'))\n"
        "assert addon.get('browser_specific_settings',{}).get('gecko',{}).get('id')==addon_id\n"
        "pathlib.Path('/home/ride-test/ublock.xpi').write_bytes(data)\n"
        "print(json.dumps({'id':addon_id,'version':meta['current_version']['version'],'sha256':hashlib.sha256(data).hexdigest()}))\n"
        "PY"
    )
    firefox_bin = vm.run("readlink -f \"$(command -v firefox)\"").stdout.strip()
    distribution_dir = str(Path(firefox_bin).parent / "distribution" / "extensions")
    distribution_dir_q = shlex.quote(distribution_dir)
    vm.run(
        "sudo mkdir -p /usr/lib64/mozilla/extensions/" + APP_ID + " " +
        distribution_dir_q + " && " +
        "sudo install -o root -g root -m 0644 /home/ride-test/ublock.xpi " +
        "/usr/lib64/mozilla/extensions/" + APP_ID + "/" + ADDON_ID + ".xpi && "
        "timeout 50 firefox --headless --no-remote --profile "
        "/home/ride-test/.mozilla/firefox/probe-global about:blank; rc=$?; "
        "test \"$rc\" -eq 124"
    , timeout=70)
    global_state = vm.run(
        "jq -r '.addons[]?.id' /home/ride-test/.mozilla/firefox/"
        "probe-global/extensions.json 2>/dev/null | grep -Fx " +
        json.dumps(ADDON_ID), check=False)
    vm.run("! pgrep -x firefox")
    vm.run(
        "sudo rm /usr/lib64/mozilla/extensions/" + APP_ID + "/" + ADDON_ID +
        ".xpi && sudo install -o root -g root -m 0644 /home/ride-test/ublock.xpi " +
        distribution_dir_q + "/" + ADDON_ID + ".xpi && "
        "timeout 50 firefox --headless --no-remote --profile "
        "/home/ride-test/.mozilla/firefox/probe-distribution about:blank; rc=$?; "
        "test \"$rc\" -eq 124"
    , timeout=70)
    distribution_state = vm.run(
        "jq -r '.addons[]?.id' /home/ride-test/.mozilla/firefox/"
        "probe-distribution/extensions.json 2>/dev/null | grep -Fx " +
        json.dumps(ADDON_ID), check=False)
    vm.run("! pgrep -x firefox")
    vm.run(
        "sudo rm -f " + distribution_dir_q + "/" + ADDON_ID + ".xpi " +
        "/usr/lib64/mozilla/extensions/" + APP_ID + "/" + ADDON_ID + ".xpi && " +
        "timeout 50 firefox --headless --no-remote --profile "
        "/home/ride-test/.mozilla/firefox/probe-global about:blank; rc=$?; "
        "test \"$rc\" -eq 124"
    , timeout=70)
    global_after_remove = vm.run(
        "jq -r '.addons[]?.id' /home/ride-test/.mozilla/firefox/"
        "probe-global/extensions.json 2>/dev/null | grep -Fx " +
        json.dumps(ADDON_ID), check=False)
    vm.run("! pgrep -x firefox")
    vm.run(
        "sudo rm -f " + distribution_dir_q + "/" + ADDON_ID + ".xpi && "
        "timeout 50 firefox --headless --no-remote --profile "
        "/home/ride-test/.mozilla/firefox/probe-distribution about:blank; rc=$?; "
        "test \"$rc\" -eq 124"
    , timeout=70)
    distribution_after_remove = vm.run(
        "jq -r '.addons[]?.id' /home/ride-test/.mozilla/firefox/"
        "probe-distribution/extensions.json 2>/dev/null | grep -Fx " +
        json.dumps(ADDON_ID), check=False)
    vm.run("! pgrep -x firefox")
    vm.run(
        "test \"$(cat /home/ride-test/.mozilla/firefox/"
        "probe-global/user-data.txt)\" = preserve"
    )
    observed = {
        "global_mozilla_directory": {
            "installed": global_state.returncode == 0,
            "removed_after_source_removal": global_after_remove.returncode != 0,
        },
        "firefox_distribution_directory": {
            "installed": distribution_state.returncode == 0,
            "removed_after_source_removal": distribution_after_remove.returncode != 0,
        },
    }
    print(json.dumps(observed, sort_keys=True))
    assert any(
        result["installed"] and result["removed_after_source_removal"]
        for result in observed.values()
    ), observed
