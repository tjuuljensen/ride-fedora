# Fedora DNF5 automatic-update plugin package acceptance

Status: **PASS on Fedora 44 Server x86_64; opt-in candidate**.

Acceptance run: 2026-11-02 on pinned target `fedora-44-server-x86_64`, using
TCG. Image SHA-256:
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.
Transcript:
`.acceptance-runs/generic-server-03-autoupdate-acceptance-final/transcript.jsonl`.
Transcript SHA-256:
`de1c8299baffcd9cdb8e0a9c9f49e21cac6fc8080de1fbe4dbbff2830f0d861a`.
Source bundle SHA-256:
`8e93f719c0fcc10f1e83896c3383b8fae8c7956546fed97104e83888deba35a6`.

`package.dnf5-plugin-automatic` is a Fedora 44 Server x86_64 opt-in candidate. It
installs the signed Fedora RPM that supplies the DNF5 automatic command and
timer/service units. Installing it does not enable the timer. Removing the
new RPM does not downgrade existing DNF/libdnf packages that DNF upgrades in
the same transaction.

The lifecycle verified candidate gating, signed RPM installation and `rpm -V`,
repeat, status, and removal of `dnf5-plugin-automatic`. The DNF transaction
upgraded eight existing RPMs from 5.4.1.0 to 5.4.6.0: `dnf5`, `dnf5-plugins`,
`dnf5daemon-server`, `libdnf5`, `libdnf5-cli`,
`libdnf5-plugin-appstream`, `libdnf5-plugin-expired-pgp-keys`, and
`python3-libdnf5`. It also installed the weak dependency
`libdnf5-plugin-systemd-inhibit`. Removing the plugin did not downgrade those
upgrades. The before/after RPM name-and-architecture comparison found no
pre-existing identity removed.

Source: [Fedora 44 package record](https://packages.fedoraproject.org/pkgs/dnf5/dnf5-plugin-automatic/fedora-44.html).
