# Fedora 44 Server base package pilot

Date: 2026-10-30. Target: Fedora 44 Server x86_64 with
`VARIANT_ID=server`, default `fedora-rpm` source, and system scope. The
[locally built image](fedora-44-server-image.md) SHA-256 is
`efb75956d6dbde0801059fdac4a8a1451f06ecc843344ecdb71bb3e8d247af90`.
The harness verified that digest and the guest's distro, release, edition,
and architecture before testing. Source revision:
`0bfd3c02350c85069c85b3b28457c2396e827d67` with uncommitted changes;
catalog SHA-256:
`27e2a8310a56123488a25a3c9dd74631365e4acbe8085e542247d9280f4d6bf5`.
All operations were candidates at pilot time, pending exact-diff review. No host-specific
server behavior was moved from `network-devices`.

| Operation or profile | Focused automated result | Disposable overlay and JUnit |
| --- | --- | --- |
| `package.less` edition gate | PASS: Server plan allowed; test-only other edition refused by plan, show, and status without a journal. | `20261030T075503Z-test-guest-variant-scope-matches-catalog-c34e6508`; `.acceptance-runs/server-less.xml` |
| `package.less` lifecycle | PASS: installed base observed in read-only plan; removed in disposable overlay; RIDE installed it, repeat unchanged, status and signed RPM/files verified, dry-run restore and restore recovered inventory, explicit install/remove recovered inventory. | `20261030T075528Z-test-package-apply-repeat-status-restore-and-remove-ca299d76`; `.acceptance-runs/server-less.xml` |
| `package.less` injected failure | PASS: first step changed, later missing package failed, journal recorded both; restore recovered inventory. | `20261030T075630Z-test-partial-failure-records-completed-step-and-can-restore-78ec4dfa`; `.acceptance-runs/server-less.xml` |
| `package.openssh-clients` edition gate | PASS: Server plan allowed; test-only other edition refused without a journal. | `20261030T075751Z-test-guest-variant-scope-matches-catalog-a759fca4`; `.acceptance-runs/server-openssh-clients.xml` |
| `package.openssh-clients` intact client | PASS: read-only plan, two unchanged apply journals, status, `ssh -V`, signed RPM/files, unchanged inventory and `/etc/ssh/ssh_config`, active SSH server, refused remove. | `20261030T075815Z-test-installed-only-package-keeps-existing-client-and-server-928cb116`; `.acceptance-runs/server-openssh-clients.xml` |
| `package.openssh-clients` repair and failure | PASS: client removed with test-only `rpm -e --nodeps` in a disposable overlay, then RIDE reinstalled it before an injected later failure. Journal recorded changed and failed steps with `recovery: none`; `dnf check`, RPM signature/files, `ssh -V`, repeat apply, status, SSH server, and refused restore/remove all passed without later inventory or config change. | `20261030T075842Z-test-installed-only-package-repairs-absence-and-refuses-inverse-76f28e72`; `.acceptance-runs/server-openssh-clients.xml` |
| `server-base` profile | PASS in both selected pilot suites: exactly `package.less` and `package.openssh-clients` planned as installed; apply journal was unchanged in profile order; individual status, inventory, SSH config, and active server matched. | `20261030T075719Z-test-server-base-profile-smoke-4a95e533`, `20261030T075933Z-test-server-base-profile-smoke-0db9769d`; both JUnit files above |

The `package.less` suite reported 4 passed and 3 inapplicable scenarios
skipped in 160.57 seconds. The OpenSSH suite reported 4 passed and 3
inapplicable scenarios skipped in 126.76 seconds. Scenario selectors skipped
before VM startup. The Workstation/Cloud DNF handler behavior is unchanged,
and this Server run independently checked the exact edition, package
lifecycle or installed-only behavior, and profile interaction. The OpenSSH
artificial absence is recovered by discarding its overlay; it is never a
production removal procedure. No manual session was needed.

The later per-operation [less](package.less.md) and
[OpenSSH](package.openssh-clients.md) acceptance records review the source diff.
The owner confirmed no non-disposable v3 runs before promotion.

Post-commit source check: after candidate commit `17849c4`, compared all 11
bundled runtime source files (`ride.sh`, catalog, profiles, `lib/v3`, and
requirements) in the Server `less` lifecycle and OpenSSH repair overlay
archives against the committed working files. No bytes differed. The only
remaining working-tree change was the unrelated deletion of
`docs/v3-migration.md`, which was not in either runtime bundle. This confirms
that the pilot ran the same runtime source as the committed candidate; the
dated metadata still honestly records the working tree as dirty at run time.
