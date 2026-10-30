# Provider foundation batch 08: Eza source and destination ownership

Status: **unresolved**, 2026-10-30. `InstallEza` installs the Fedora RPM,
while `InstallEzaGitHub` obtains a release artifact for `/usr/local/bin`.
`RemoveEza` removes the Fedora package and also deletes
`/usr/local/bin/eza` without checking its owner. Review each acquisition
source, artifact verification, destination, detection, product conflict,
and inverse before mapping the two v2 outcomes to v3. An installed and a
portable deployment may coexist only after that ownership review; neither
may delete the other's unowned artifact.
