# Glances native RPM acceptance

Status: **PASS — supported on Fedora 44 Workstation and Server x86_64**.

Disposable VM run: **PASS** on Fedora 44 Workstation x86_64 for
`package.glances`.

`package.glances` replaces the v2 `TecmintMonitorSh` downloader with Fedora's
signed Glances package. The v2 script was a one-shot health summary; Glances
provides a terminal monitoring interface with CPU, memory, disk, process, and
network views. This operation installs only the package. The Server Web UI is
selected separately through the opt-in `fedora-server-glances-web` profile.

## Completion checks

- On disposable Fedora 44 Workstation x86_64, run `plan`, apply through its
  opt-in profile, repeat, inspect status, verify the RPM, and
  remove it only if it was newly installed by the test.
- Confirm package installation does not enable or start `glances.service` and
  does not open firewall ports.
- Run `glances --version` and a 20-second non-interactive
  `PYTHONUNBUFFERED=1 timeout 20 glances --disable-process --stdout
  cpu.user,mem.used,load` smoke check. Disabling process enumeration keeps the
  TCG check focused on the requested metrics. Since stdout mode emits one line
  per refresh, accept timeout exit 124 only when all three metrics appear;
  verify restore leaves `/etc/glances`
  and a seeded user configuration untouched. Confirm the service remains
  inactive/disabled and firewalld exposes no new port.
- Keep the package out of base profiles; select it through its opt-in profile.

The completed run used the pinned Fedora 44 Workstation x86_64 image with
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
and QEMU TCG with 4 CPUs and 6144 MiB. It passed the gate, apply, repeat,
status, signature and RPM file verification, version and metrics checks,
service/firewall checks, and exact restore. Full metadata, transcript, and
serial output are preserved in `.acceptance-runs/resolution-review-01-glances/`;
the transcript SHA-256 is
`ecfe4d97f13e08a9c49e63314fc88501a8f1e41e9c6e1c7cf7d7489610510e44`.

The Fedora 44 package source is the distribution repository, whose RPM
signature is verified by DNF. No publisher download or Python environment is
managed by RIDE. Upstream describes Glances as LGPL-3.0 and documents the
terminal interface and its non-interactive output mode.
The operation is supported on this exact target and selected by the opt-in
`fedora-workstation-glances` profile.

## Fedora 44 Server x86_64 package evidence

The Server package and service pilot passed. Fedora's signed repository
installed `glances-4.5.7-1.fc44` and its Web dependencies. With a valid
pre-existing `/etc/glances/glances.conf`, RPM preserved the original bytes and
placed the packaged default in `.rpmnew`; removal retained the original bytes
as `.rpmsave`. See [Glances Web service acceptance](setting.glances-web-service.md)
for lifecycle evidence. H102 tracks restoring the prior config at its original
path during package removal.
