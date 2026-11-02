# Brave Browser RPM acceptance

Status: **operable opt-in candidate**, accepted on Fedora 44 Workstation
x86_64 on 2026-11-01.

VM acceptance **passed** for operation `package.brave` on Fedora 44
Workstation.

The handler validates the official Brave release signing-key material, creates
an exact RIDE-owned DNF5-compatible repo file with `gpgcheck=1`, and installs
only from the declared repo ID. Removing Brave leaves the user profile and
the global RPM trust key untouched. A pre-existing exact repo file is reused
and preserved; conflicting content is refused.

Mocked tests cover owned install/repeat/remove, conflict refusal, preserving a
pre-existing repo file, and preserving operator edits during cleanup. The
shared disposable-VM test checks `brave-browser --version`, repeat, removal
while Code remains installed, and seeded profile preservation.

The shared test passed the candidate gate, signed RPM install,
`brave-browser --version`, repeat apply, removal, repo cleanup, preservation of
Code during Brave removal, and seeded user-file preservation. See the [batch
transcript](../../.tmp-vm-acceptance-publisher-03-from-repo-retry/fedora-44-workstation-x86_64/20261101T161819Z-test-publisher-repository-rpm-lifecycle-and-user-profile-recovery-92c61583/transcript.jsonl)
(SHA-256 `6084265f71cc0fd5db3926a0cc5a01921d4c85fe3428cc84e07576caa2696cb7`)
and [batch record](../migrations/publisher-apps-03.md).
