# `package.handbrake-cli` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 RPM Fusion Free publishes the HandBrake CLI in the `HandBrake` RPM
(1.11.2 in the current Fedora 44 repository); the GUI is a separate
`HandBrake-gui` RPM. The accepted
[`rpmfusion` profile](../migrations/provider-foundation-02.md) establishes
Fedora-distributed signing-key trust and owned repository configuration. The
operation selects `rpmfusion-free-updates` explicitly and does not fall back
to Fedora or another repository. See the [RPM Fusion package index](https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/h/)
and [HandBrake project](https://handbrake.fr/).

The opt-in profile contains only `package.handbrake-cli`; apply the accepted
`rpmfusion` profile first. The focused VM lifecycle passed candidate refusal,
plan, RPM Fusion origin/signature, `rpm -V`, the `HandBrakeCLI` executable and
version, status, unchanged repeat, restore, explicit install/remove, RPM
inventory recovery, scriptlet, capability, and systemd-unit checks. No media
was encoded or read. CLI package lifecycle is operable on the declared target;
the GUI/Flatpak deployment and product-conflict review remains H067.

VM evidence: Fedora 44 Workstation x86_64; pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`;
overlay `20261101T141928Z-test-package-apply-repeat-status-restore-and-remove-a18728a1`;
catalog SHA-256
`e27bbc6c962f229e681700f11ca3a52a837ee602c5b0179b6aeb4aaa222f2bcf`;
transcript [transcript.jsonl](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-provider-07-complete-rerun/fedora-44-workstation-x86_64/20261101T141928Z-test-package-apply-repeat-status-restore-and-remove-a18728a1/transcript.jsonl)
SHA-256 `2ebd80854f76d977a8391aeb5514f27f43b67a26f617b057fabf152efac42e77`.
The test installed the signed `HandBrake` RPM and dependencies, verified the
CLI and candidate status, repeated without changes, restored, then exercised
explicit install/remove. All package RPMs returned to baseline. RPM Fusion's
imported signing-key record remains in the RPM database after removal; the
test explicitly permits only this expected trust residue.
