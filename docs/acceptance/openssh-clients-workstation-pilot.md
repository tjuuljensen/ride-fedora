# Fedora 44 Workstation OpenSSH client pilot

Date: 2026-10-30. Target: pinned Fedora 44 Workstation x86_64 image from
[the image record](fedora-44-workstation-image.md). Operation:
`package.openssh-clients`, default `fedora-rpm` source, system scope.
The Fedora [subpackage record](https://packages.fedoraproject.org/pkgs/openssh/openssh-clients/)
identifies the client tools, license, and Fedora 44 build. The v3 catalog
declares Workstation only; Server is awaiting its own image and evidence.

Initial run: `/tmp/ride-acceptance-runs/fedora-44-workstation-openssh-clients.xml`.
The edition-gate scenario passed. Lifecycle and partial-failure scenarios
failed during disposable overlay preparation, before RIDE applied a change.
Both attempted `dnf remove openssh-clients` after observing it installed in
the base. DNF refused because installed `gcr` requires `ssh-add` and
`ssh-agent`, and GNOME Shell requires `gcr`. The failures remain recorded as
FAIL; repeating that removal would not test a valid inverse.

This finding changed the completion criterion. The catalog now declares
installed-only state and `recovery: none` for this Workstation operation.
Removing the package would break the GNOME dependency chain; an automatic
inverse is unavailable. The deliberately absent state below exists only in a
disposable overlay. Discarding that overlay is its recovery. No production host
was changed.

Focused rerun: `/tmp/ride-acceptance-runs/fedora-44-workstation-openssh-clients-installed-only.xml`
(3 passed, 2 inapplicable reversible-package scenarios skipped, 106.22 seconds).
The harness verified base image SHA-256
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`
and guest `ID=fedora`, `VERSION_ID=44`, `VARIANT_ID=workstation`, and
`x86_64`. Source revision: `0bfd3c02350c85069c85b3b28457c2396e827d67`;
catalog SHA-256: `0a105c19f6d7166d6e59e0810eea96aef7f5ce53feb92b17a8f4a78eae13029d`.
The source was uncommitted during the run, so this was pilot evidence pending
review. Catalog status was `candidate` during the pilot; the later
[acceptance record](package.openssh-clients.md) documents its supported state.

| Scenario | Result | Disposable overlay |
| --- | --- | --- |
| Workstation edition gate | PASS: declared plan allowed; test-only other edition rejected by plan, show, and status without a journal. | `20261030T074059Z-test-guest-variant-scope-matches-catalog-4ca919ff` |
| Intact Workstation client | PASS: read-only plan, unchanged apply and repeat, installed status, `ssh -V`, signed RPM and file verification, unchanged package inventory and `/etc/ssh/ssh_config` checksum, active SSH server, and refused remove. | `20261030T074126Z-test-installed-only-package-keeps-existing-client-and-server-c33dc9b7` |
| Artificially absent client | PASS: test-only `rpm -e --nodeps` removed the client while leaving `gcr`, GNOME Shell, and SSH server; RIDE installed it before an injected later package failure. The failed journal recorded changed and failed steps with `recovery: none`. `dnf check`, signed RPM and file verification, `ssh -V`, unchanged repeat, installed status, and active SSH server passed. Restore and remove refused without changing package inventory or SSH configuration. | `20261030T074158Z-test-installed-only-package-repairs-absence-and-refuses-inverse-5ad1de81` |

The generic reversible-package scenarios were skipped before VM startup by
the catalog recovery marker. They do not count as tests of this installed-only
operation. No desktop manual session was needed for these command-line tools.
The later [acceptance review](package.openssh-clients.md) checked the exact
source diff. The owner confirmed no non-disposable v3 runs before promotion.
