"""Disposable Fedora lifecycle for the pinned legacy Galleta CLI."""

def test_galleta_pinned_user_binary_lifecycle(vm):
    profile = vm.put_json("galleta-profile", {
        "schemaVersion": 1,
        "id": "acceptance-galleta",
        "description": "Test the pinned Galleta CLI lifecycle.",
        "operations": [{"id": "package.galleta", "state": "installed"}],
    })
    assert vm.run("test ! -e /home/ride-test/.local/bin/galleta").returncode == 0
    client = "/home/ride-test/ride/ride.sh"
    plan = vm.run(f"{client} plan --profile {profile}")
    assert "package.galleta" in plan.stdout and "candidate" in plan.stdout
    refused = vm.run(f"{client} apply --profile {profile}", check=False)
    assert refused.returncode != 0 and "candidate without VM acceptance" in refused.stderr
    applied = vm.run(f"{client} apply --profile {profile} --allow-candidate")
    assert "package.galleta" in applied.stdout
    binary = "/home/ride-test/.local/bin/galleta"
    vm.run(f"test -x {binary}")
    deps = vm.run(f"ldd {binary}").stdout
    assert "not found" not in deps
    status = vm.run(f"{client} status package.galleta").stdout
    assert "package.galleta\tdebian-galleta-pinned\tinstalled\tcandidate" in status
    repeated = vm.run(f"{client} apply --profile {profile} --allow-candidate")
    assert "unchanged package.galleta" in repeated.stdout
    removed = vm.run(f"{client} remove package.galleta --allow-candidate")
    assert "package.galleta" in removed.stdout
    assert vm.run("test ! -e /home/ride-test/.local/bin/galleta").returncode == 0
    assert vm.run("test ! -e /home/ride-test/.local/share/ride-fedora/owned-tools/package.galleta.json").returncode == 0
    assert vm.run(f"{client} status package.galleta").stdout.splitlines()[-1].split("\t")[2] == "absent"
