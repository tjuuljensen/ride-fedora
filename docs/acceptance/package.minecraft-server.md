# `package.minecraft-server` acceptance

Status: **PASS — Fedora 44 Server x86_64, candidate lifecycle**.

The opt-in `fedora-server-java-25-runtime` system profile installs Fedora's
OpenJDK 25 headless runtime. The separate user-scope
`fedora-server-minecraft-server` profile installs the official Mojang 26.3
Java server JAR. Separate profiles preserve RIDE's system/user scope rule.
The JAR is pinned to Mojang's
content-addressed SHA-1 URL; RIDE verifies the object digest and records an
observed SHA-256 for later integrity checks.

The focused disposable-VM test for `package.java-25-openjdk-headless` and
`package.minecraft-server` seeded a world file, `server.properties`, and
`eula=false`. It passed both candidate gates, runtime and artifact install,
repeat, installed status, exact artifact removal, runtime removal, and exact
preservation of all three files. It did not start the server or accept its
EULA. No systemd service or firewall rule was created.

The run used the pinned Fedora 44 Server x86_64 image with SHA-256
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90` under
QEMU TCG. Full metadata, transcript, and serial output are preserved in
`.acceptance-runs/generic-server-20-minecraft/`; the transcript SHA-256 is
`0d8e880636217309ecb0874ba334ee9c6d1f3f53f77f91ff10df0a8301a1a7c5`.

```sh
python3 -m pytest tests/acceptance/test_minecraft_server.py \
  --vm-target fedora-44-server-x86_64 \
  --vm-pilot package.minecraft-server \
  --vm-image /path/to/fedora-44-server.qcow2 \
  --vm-accel tcg \
  --vm-output /tmp/ride-minecraft-server-acceptance
```

The Java RPM and official Mojang JAR remain opt-in candidates after the exact
target happy path. Service, EULA, world initialization, and world upgrade
behavior are tracked separately under H097.
