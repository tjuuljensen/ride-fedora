# `package.exfatprogs` Fedora Cloud Base pilot

Status: **PASS as a Cloud Base pilot on 2026-10-30; operation remains `candidate`.**
This is package-handler evidence, not Fedora Workstation or Server acceptance.

| Field | Evidence |
| --- | --- |
| Target | Fedora 44 Cloud Base, x86_64; `fedora-44-cloud-x86_64` |
| Image | `Fedora-Cloud-Base-Generic-44-1.7.x86_64.qcow2`; SHA-256 `28680fe5b371a5a82ebf43a31926e086a168e59949d03969c5093e7071f90b7f` |
| Source | `f67a502c88fe90b327fbab410734b4b5469f9691` plus uncommitted VM seed and acceptance assertion fixes; catalog SHA-256 `3d01f975860b02f7f87b4ec06bb6824c3b8df269eaab8bdfb0ca90a564a72dd0` |
| Profile | Disposable `acceptance` profile selecting `package.exfatprogs` as `installed`, default `fedora-rpm` source |
| Runner | `pytest tests/acceptance -v -p no:cacheprovider --rootdir=. --vm-target fedora-44-cloud-x86_64 --vm-image <verified-local-image> --vm-output /tmp/ride-acceptance-runs`; the local image path is omitted from this public record |
| Result | Two tests passed; JUnit: `/tmp/ride-acceptance-runs/fedora-44-cloud-updated-results.xml` |
| Review | Automated assertions passed; owner review and edition-specific acceptance remain pending |

The lifecycle scenario began with `exfatprogs` absent. Read-only `plan` left it
absent; `apply` installed it; repeated `apply` recorded `unchanged`; `status`
reported installed; `restore --dry-run` and `restore` returned it to absent;
duplicate restore was refused; explicit `install` and `remove` completed.
The installed RPM had an RSA/SHA-256 signature from Fedora key ID
`dbfcf71c6d9f90a6`, and `rpm -V exfatprogs` reported no modified files.
The complete RPM package inventory, including versions, matched the baseline
after both restore and explicit remove.

The failure scenario added a deliberately nonexistent package only to a guest
catalog. The journal recorded the completed `package.exfatprogs` step and the
failed step; restore removed `exfatprogs` and returned the package inventory to
baseline. Both guests reported `cloud-init status --wait` exit 0 after the seed
stopped requesting an early hostname change.

Retained overlay IDs are
`20261030T062416Z-test-package-apply-repeat-status-restore-and-remove-f08dbf49`
and
`20261030T062445Z-test-partial-failure-records-completed-step-and-can-restore-9dc80c48`.
Their `metadata.json` and `transcript.jsonl` files are under
`/tmp/ride-acceptance-runs/fedora-44-cloud-x86_64/`; the directory contains
disposable SSH private keys and must be reviewed before sharing. The test
runner stopped both VM processes and retained their overlays.

Next: repeat the package pilot on Fedora 44 x86_64 Workstation, review the
current Windows schema and package behavior for this batch, and record a
reproducible committed revision before considering any supported target row.
