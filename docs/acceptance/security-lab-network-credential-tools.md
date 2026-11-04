# Security Lab network credential tools acceptance

Batch 06S covers Hydra, Medusa, Ncrack, dsniff, and Ettercap as Fedora RPM
presence operations in the opt-in `fedora-security-lab-network-credential-tools`
profile. Current upstream and license metadata are recorded in the [batch
record](../migrations/provider-foundation-06.md).

The pinned Fedora 44 Workstation x86_64 candidate lifecycle passed on
2026-10-31. Candidate refusal, plan, apply, signatures, root-run `rpm -V`,
status, repeat apply, restore, and package identity recovery passed. Hydra
upgraded preinstalled `expat` from 2.7.3-2.fc44 to 2.9.0-1.fc44 and added 14
dependencies. dsniff added `libdb` and `libnids`; Medusa, Ncrack, and Ettercap
added no dependencies. Restore removed all new packages and retained Fedora's
expat update because RPM downgrade is not a safe recovery. No other existing
RPM changed. Scripts and file-capability metadata were inspected. No login was
attempted and no traffic was captured or intercepted. Transcript and overlay:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06s/fedora-44-workstation-x86_64/20261031T143242Z-test-fedora-security-lab-network-credential-batch-and-profile-217e2d1b/`.

All operations remain opt-in and candidate-gated pending H044 review of
authorized targets, attempt limits, captured data handling, and recovery.
Catalog operation IDs in this accepted profile: `package.dsniff`, `package.ettercap`, `package.hydra`, `package.medusa`, `package.ncrack`.
