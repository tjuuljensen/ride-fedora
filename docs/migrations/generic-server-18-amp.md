# Generic Server 18: AMP

Status: **operable opt-in candidate** on Fedora 44 Server x86_64.

The owner kept v2 `InstallAMP`. Its legacy implementation runs CubeCoders'
mutable QuickStart script, which installs the manager, creates an `amp`
account and default ADS controller, enables services, and changes firewall
rules. The current publisher RPM was inspected before migration: it is
unsigned, and its package scriptlets also perform host-level account,
service, timer, ownership, and firewall changes. A first signed-repository
approach correctly failed verification and was not retried unchanged.

## v3.0 contract

- `package.amp-installer` is available through the opt-in
  `fedora-server-amp` profile and requires `--allow-candidate`.
- The handler pins CubeCoders' HTTPS RPM URL, package identity `2.8.0.10-2`,
  and SHA-256 `c766e78308df4ff29d703081b4e2477d70822deb5344c985a3502a2306d0396e`.
  This is digest verification of an unsigned RPM, not a publisher signature.
- Both install and removal use DNF `tsflags=noscripts`, preventing the RPM
  scriptlets from creating users, enabling units/timers, changing ownership,
  or altering firewall rules. RIDE reloads systemd's unit inventory only.
- Install refuses pre-existing AMP-owned paths. Removal refuses if known AMP
  units are active or enabled. Restore removes the package and its package
  files while preserving the operator's account and private AMP data.
- RIDE does not create an ADS instance, manage credentials or license inputs,
  select runtimes, configure HTTPS or ports, alter firewall policy, or migrate
  controller and game data.

## Completion checks

The acceptance test defines the package-only checks before apply. It verifies
candidate gating, plan, pinned digest and package identity through install,
repeat, status, restore, inactive and disabled AMP units, and preservation of
a seeded account, private data marker, and firewalld state. DNF refreshed Fedora
metadata during the install, taking about two minutes; the package transaction
then completed successfully. See the [acceptance record](../acceptance/package.amp-installer.md)
and [retained VM transcript](../../.acceptance-runs/fedora-44-server-x86_64/20261102T100243Z-test-amp-manager-rpm-preserves-operator-home-and-firewall-e23e6e73/transcript.jsonl).

Signed upstream publication, future update handling, ADS/controller setup,
private credentials and license, service/timer activation, firewall exposure,
and real instance-data migration remain in H106. Windows has no shared AMP
package operation; this Fedora-specific contract is an intentional difference.
