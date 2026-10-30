# Provider foundation batch 07: HandBrake RPM Fusion source

Status: **unresolved**, 2026-10-30. The v2 pair installs and removes
`HandBrake` with DNF. This review has not established a Fedora repository
build; the [RPM Fusion Fedora 44 package index](https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/h/)
lists `HandBrake` and a separate GUI RPM. Before a runnable v3 operation, review the current
publisher package and license, repository installation and signature trust,
dependency behavior, exact package name, detection, and recovery. Coordinate
with the separate RPM Fusion repository-source outcome; do not silently add a
third-party repository to a base profile.
