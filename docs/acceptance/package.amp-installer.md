# AMP instance manager package acceptance

Target: Fedora 44 Server x86_64, disposable QEMU guest, TCG acceleration.

Result: **PASS** for `package.amp-installer` on the declared target.

CubeCoders' current `ampinstmgr` RPM is unsigned. RIDE does not claim publisher
signature verification. The candidate pins package version `2.8.0.10-2`, the
official HTTPS artifact URL, and SHA-256
`c766e78308df4ff29d703081b4e2477d70822deb5344c985a3502a2306d0396e`. The
handler verifies the digest and RPM identity before installation, then uses
DNF's `tsflags=noscripts` for both install and removal. This suppresses the
RPM scriptlets that would otherwise create accounts, enable AMP services and
timers, recursively change `/opt/cubecoders` ownership, and modify firewall
state. RIDE only reloads systemd's unit inventory after package changes.

The focused lifecycle checks candidate refusal without `--allow-candidate`,
plan, install, repeat, status, and restore. Before apply, the test creates an
`amp` account and private instance-data marker. It verifies the account ID,
marker bytes, and firewalld configuration survive both package installation
and removal. It also checks AMP units remain disabled and inactive after
install and that package-owned paths disappear on restore. Installation
refuses existing AMP paths, and removal refuses active or enabled AMP units.

This package operation does not create an ADS controller, set credentials,
activate a license, select container or Java runtimes, configure HTTPS, expose
ports, or migrate existing AMP data. Those remain operator-managed.

Evidence: [VM transcript](../../.acceptance-runs/fedora-44-server-x86_64/20261102T100243Z-test-amp-manager-rpm-preserves-operator-home-and-firewall-e23e6e73/transcript.jsonl)
and the corresponding retained overlay, metadata, and console logs.
