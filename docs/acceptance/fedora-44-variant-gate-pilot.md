# Fedora 44 edition target gate pilot

Date: 2026-10-30. Source revision: `0bfd3c02350c85069c85b3b28457c2396e827d67`
with uncommitted changes. Catalog SHA-256:
`884bcf10405caabee27b8d8ae32a66a06f309680a20339f64d6b6e50c5f6b3b0`.
The catalog now declares `variantIds` for the two operations with earlier
target-specific lifecycle evidence. `package.exfatprogs` declares Cloud Base
and Workstation; `package.less` declares Workstation. Both remain `candidate`.

Each focused disposable VM test checked the pinned image and actual
`VARIANT_ID`, planned the declared operation successfully, then used a
test-only catalog restricted to a different edition. That plan failed closed;
`show` and unfiltered `status` reported `unsupported`, and no run journal was
created. The test-only catalog was not added to the published catalog.

| Target and operation | Result | Overlay and JUnit |
| --- | --- | --- |
| Fedora 44 Workstation x86_64, `package.exfatprogs` | PASS | `20261030T072835Z-test-guest-variant-scope-matches-catalog-f5624ba7`; `/tmp/ride-acceptance-runs/fedora-44-workstation-variant-exfatprogs.xml` |
| Fedora 44 Cloud Base x86_64, `package.exfatprogs` | PASS | `20261030T072836Z-test-guest-variant-scope-matches-catalog-d0de33d4`; `/tmp/ride-acceptance-runs/fedora-44-cloud-variant-exfatprogs.xml` |
| Fedora 44 Workstation x86_64, `package.less` | PASS | `20261030T072927Z-test-guest-variant-scope-matches-catalog-847a6fcf`; `/tmp/ride-acceptance-runs/fedora-44-workstation-variant-less.xml` |

The [Workstation lifecycle pilot](workstation-package-batch-1-pilot.md) and
[Cloud Base handler pilot](package.exfatprogs-cloud-base-pilot.md) remain valid
for the unchanged DNF handler. The new target behavior was checked separately
on the exact editions rather than repeating the full package lifecycle.
Mocked tests also covered missing variants, provider conflict selection,
supported-row validation, and fail-closed restore after a target declaration
change. No manual session was needed.

Changing a target row changes its recorded source signature. A run created
under the older catalog cannot be restored with the narrowed catalog; the
mocked recovery test confirms restore succeeds again with the original
catalog. Before publishing a supported row, inventory any non-disposable
candidate runs and recover them with their original catalog or record a
reviewed alternative. The [Windows alignment review](../windows-alignment.md#linux-edition-target-gate-2026-10-30)
records why this Linux edition field differs from Windows targeting. Reviewer:
pending. This pilot does not promote either operation.
