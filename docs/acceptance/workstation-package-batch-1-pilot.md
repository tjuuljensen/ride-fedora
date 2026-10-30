# Fedora 44 Workstation package batch 1 pilot

Date: 2026-10-30. Target: Fedora 44 Workstation x86_64, `VARIANT_ID=workstation`,
default `fedora-rpm` source, system scope. The disposable guest was built with
the [pinned installer recipe](fedora-44-workstation-image.md). Base qcow2 SHA-256:
`49bb3c03b52f43325e5c7d5cf0ec83f2222b7170e3738baad1e0e5440bb6bf9a`.
The harness verified that digest and the guest's distro, release, architecture,
and edition before copying RIDE. Source revision: `0bfd3c02350c85069c85b3b28457c2396e827d67`;
catalog SHA-256: `3d01f975860b02f7f87b4ec06bb6824c3b8df269eaab8bdfb0ca90a564a72dd0`.
The run metadata marks the source tree as having uncommitted changes, so these
results are recorded as pilot evidence pending review. The catalog status
remains `candidate`.

| Operation | Focused automated result | Disposable overlay and JUnit |
| --- | --- | --- |
| `package.exfatprogs` | PASS: plan, apply, repeated apply, status, RPM signature and files, dry-run restore, restore, explicit remove, package inventory recovery, and injected partial failure with successful restore. | `20261030T071040Z-test-package-apply-repeat-status-restore-and-remove-e0ca920e`; `20261030T071417Z-test-partial-failure-records-completed-step-and-can-restore-9db5a3bb`; `/tmp/ride-acceptance-runs/fedora-44-workstation-exfatprogs.xml` (2 passed). |
| `package.less` | PASS: plan, apply, repeated apply, status, RPM signature and files, dry-run restore, restore, explicit remove, and package inventory recovery. | `20261030T071555Z-test-package-apply-repeat-status-restore-and-remove-410a0bce`; `/tmp/ride-acceptance-runs/fedora-44-workstation-less.xml` (1 passed). |

Both packages were already installed in the pinned Workstation base. For each
scenario, the harness first observed the installed state through a read-only
plan. It then removed only that package in the disposable overlay and recorded
the post-removal RPM inventory as the install-path baseline. Recovery returned
to that baseline, including RPM versions. The original Workstation base was
never changed. `package.less` and `package.exfatprogs` use the same unchanged
`dnf-package` handler and `fedora-rpm` source. The `exfatprogs` Workstation
failure injection, together with the earlier [clean Cloud Base handler
pilot](package.exfatprogs-cloud-base-pilot.md), supplies the shared handler
failure evidence for this low-risk `less` batch. No manual session was needed
for these command-line packages.

The first Workstation boot attempt was interrupted after the harness created a
20 GiB overlay from the 40 GiB base and the guest could not find its root UUID.
The harness now inherits the base virtual size. The next run booted but failed
the old absent-package precondition; the test now handles the observed
preinstalled state. Neither earlier attempt is counted as passing evidence.

Focused host validation: six VM harness unit tests passed; Python compilation,
v3 catalog/profile validation (12 operations, three profiles), and `git diff
--check` passed. The [Windows preflight](../windows-alignment.md#fedora-workstation-package-batch-preflight-2026-10-30)
found no unexplained drift in the scoped package contract. Reviewer: pending.
Before promoting either operation, review this result against the exact source
diff and create its per-operation acceptance record with the supported target.
The catalog target predicate used distro, release, and architecture but did
not restrict edition during this lifecycle run. The subsequent
[edition gate pilot](fedora-44-variant-gate-pilot.md) added `variantIds` and
passed focused VM checks on the declared editions. Promotion still requires
operation-level review and resolution of any existing non-disposable runs
whose source signature predates the narrowed catalog targets.
