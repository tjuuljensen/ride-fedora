# Publisher application batch 16: Cheat release binary

Status: **unresolved**, 2026-10-30. The active v2 `InstallCheat` function
queries the GitHub releases API, chooses a `linux-amd64` download by text
filtering, decompresses it, and overwrites `/bin/cheat`; `RemoveCheat` deletes
that path. This is a publisher artifact workflow, not a Fedora RPM.

Before implementation, review the current upstream release, license, artifact
format and checksum or signature, destination ownership, detection, and
inverse. Define a disposable-VM happy path and recovery checks before adding
an opt-in candidate. Do not overwrite an unowned `/bin/cheat` or select the
operation in a base profile. A replacement source may be selected only after
the legacy user-visible command is compared with the current product.
