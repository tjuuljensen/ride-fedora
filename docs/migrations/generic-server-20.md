# Generic Server 20: MinecraftServer

Status: **operable opt-in candidate; Fedora 44 Server acceptance passed**.

The owner kept `InstallMinecraftServer` in v3.0. The v2 function installed an
obsolete Java 8 runtime and created a directory but did not install a server
JAR. The v3.0 path installs the server runtime and official versioned JAR as
an opt-in package profile. The RIDE-owned JAR is separate from each Minecraft
instance and its data.

## Current upstream path

The current official Java Edition release reviewed for this batch is 26.3.
Mojang's [26.3 release notes] identify the game release and link the
cross-platform server JAR. The direct
[server JAR URL](https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar)
uses Mojang's SHA-1 object identifier `33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c`.
The manager verifies that identifier before installation and records the
observed SHA-256 for later local integrity checks. Mojang's 26.1 release notes
state that Java 25 is required; Fedora 44 supplies the headless runtime as
`java-25-openjdk-headless`.

## v3.0 scope and boundaries

- `package.java-25-openjdk-headless` installs Fedora's signed runtime package.
- `package.minecraft-server` installs `server.jar` under
  `~/.local/opt/ride-fedora/minecraft-server/26.3` and records its ownership.
- The optional `fedora-server-java-25-runtime` system profile and
  `fedora-server-minecraft-server` user profile keep their scope separate;
  keep both out of `server-base`.
- RIDE does not start the JAR, create an `eula.txt`, accept Mojang's server
  EULA, create or upgrade worlds, modify `server.properties`, install a
  service, or change firewall/network settings.
- Removal deletes only the exact RIDE-owned version directory and the runtime
  package when the package transaction reports it as newly installed. It
  preserves world folders, server configuration, EULA state, and user files.

This narrows the package operation to a repeatable software deployment with
an exact inverse. Managed service startup and world lifecycle require the
separate high-risk evidence tracked by H097.

## Completion checks

The disposable Fedora 44 Server test verified candidate gates; install of
the Java 25 RPM and pinned server JAR through their separate system and user
profiles; repeat apply; installed status;
exact artifact removal; and preservation of seeded world, `server.properties`,
and `eula=false` data. It must confirm no server process, service, or open
port was created. Do not promote the source outcome until this focused target
test passed. The exact target image digest, run transcript, and serial output
are recorded in [the acceptance report](../acceptance/package.minecraft-server.md)
and `.acceptance-runs/generic-server-20-minecraft/`. Keep both operations
opt-in candidates; H097 remains the separate service and world lifecycle gate.

[Mojang Java Edition 26.3 release notes]: https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3
[Mojang Java Edition 26.1 release notes]: https://www.minecraft.net/en-us/article/minecraft-java-edition-26-1
[Fedora OpenJDK 25 headless package]: https://packages.fedoraproject.org/pkgs/java-25-openjdk/java-25-openjdk-headless/fedora-44.html
