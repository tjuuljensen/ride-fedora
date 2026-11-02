# Docker Engine v3 acceptance

The Docker v2 outcome is implemented as explicit opt-in system operation
`system.docker-engine` for Fedora 44 Workstation and Server.

## Defined completion checks

- Refuse an unowned Docker repository file, a preinstalled Docker/Moby
  package, or an existing Docker service unit before the first mutation.
- Verify the publisher signing key against the fingerprint in the reviewed
  Docker Fedora instructions, stage that exact key locally, and use the local
  key file for DNF signature checks.
- Apply the three v2 packages and start `docker.service`; repeat and status
  must report the same owned deployment. DNF weak dependencies are disabled
  so Docker Compose, Buildx, and rootless extras remain separate additions.
- The Docker daemon is started but not enabled, matching v2. After reboot,
  status reports the owned daemon as stopped; applying `configured` starts it
  again. Removal refuses a stopped daemon until it is running and RIDE can
  verify the container list.
- Refuse removal while any container is running. With no running containers,
  remove only the three declared packages, owned repository file, and RIDE
  ownership marker. Preserve `/var/lib/docker`, `/var/lib/containerd`, and
  the imported publisher key until its owned file is removed. Fedora DNF5
  verifies packages using the repository's local key file without persisting
  this publisher key in the RPM key database.
  Atomic marker and repository creation must leave no temporary hard links.
- Seed an image and a named volume with a payload on each disposable Fedora 44
  edition target. Remove and reinstall the engine, then verify the image and
  volume payload remain available.
- Verify `restore` refuses the non-restorable transaction; the explicit
  operation state `absent` is the reviewed removal path.

## Current evidence

Provider-level mocked tests cover owned apply/repeat/remove, unowned
repository refusal, running-container refusal, and volume-file preservation.
Disposable VM lifecycle evidence:

| Target | Result | Evidence |
| --- | --- | --- |
| Fedora 44 Workstation x86_64 | **PASS** | `.acceptance-runs/docker-engine-workstation-accepted/fedora-44-workstation-x86_64/20261102T064820Z-test-docker-engine-workstation-image-and-volume-recovery-35ad5190/` |
| Fedora 44 Server x86_64 | **PASS** | `.acceptance-runs/docker-engine-server-accepted/fedora-44-server-x86_64/20261102T070519Z-test-docker-engine-server-image-and-volume-recovery-c8b95970/transcript.jsonl` |

Each run installed, repeated, observed, removed, and reinstalled Docker CE;
verified RPM signatures and the exact three declared Docker packages; refused
restore as non-restorable; and preserved a seeded image ID and named-volume
payload through removal and reinstall. Removal preserved Docker data
directories and removed only the owned repository, key file, and marker. The
service was started without enabling it; stopped state and apply-to-start
behavior were checked on Workstation. DNF weak dependencies were disabled, so
Compose, Buildx, and rootless packages were not added.

The test source now checks that the owned source and marker exist after
reinstall. The Server transcript reached that final assertion after all
reinstall recovery checks passed; its original assertion expected those files
to remain absent after reinstall and was corrected. The Workstation run's
reinstall continuation is recorded in `reinstall-recovery-transcript.jsonl`
beside its transcript. These artifacts are local acceptance records and are
not tracked in Git; this document records target, result, and the checks run.
