# User default directories acceptance

`setting.user-default-directories` is an opt-in candidate for Fedora 44
Workstation x86_64. Apply creates `~/bin` and `~/git` only when absent and
records the device and inode of each created path. Restore removes only those
recorded directories when their identity is unchanged and they are empty.
Existing directories and their contents remain user-owned. Symlinks, path type
conflicts, changed identities, malformed ownership state, and nonempty created
directories fail closed.

The mocked lifecycle suite and Fedora 44 Workstation x86_64 TCG acceptance
cover existing-directory preservation, repeat apply, symlink refusal before
side effects, and nonempty-directory recovery. Fedora 44 Workstation VM
acceptance passed: the opt-in profile applied and removed successfully while
preserving a seeded `~/git` file.

- Transcript: `.tmp-vm-acceptance-desktop-user-01-directories-fixed/fedora-44-workstation-x86_64/20261101T194723Z-test-user-default-directories-lifecycle-and-recovery-fa7a4d33/transcript.jsonl`
- Transcript SHA-256: `bd6ed52b90b0e7a251f6210215be762e18a562f6114259946f7004ad014beab1`
- VM image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`
- Catalog SHA-256: `b082751c382af1d02f53ae2bb319bb77b0e2e22e2fb4d56976f3fca0680dce6e`
