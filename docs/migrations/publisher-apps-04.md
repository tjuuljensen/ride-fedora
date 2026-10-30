# Firefox extension policy tool handoff

Status: **documented non-runnable replacement for v3.0**, 2026-10-30.
This isolated active-preset outcome maps `InstallFirefoxAddons` and
`RemoveFirefoxAddons`. The current v2 functions already delegate to the
repository's maintained [`manage-firefox-extensions.py`](../../tools/manage-firefox-extensions.py).
That tool validates a manifest, checks Mozilla Add-ons and XPI IDs before
install, merges `ExtensionSettings` into `/etc/firefox/policies/policies.json`,
backs up prior policy, and records ownership. Removal writes blocked
tombstones for Firefox to process; a separate finalizer removes them.

## Completion criteria defined before a runnable v3 operation

- Represent the exact manifest and policy ownership in the v3 catalog and
  run journal. Detect the current managed policy without reading a user
  profile. Refuse conflicts with unrelated administrator policy.
- Test online acquisition failure, interrupted writes, old-policy restore,
  and two-step Firefox removal against seeded policy and profile state.
  Include a disposable Fedora 44 x86_64 Workstation lifecycle and one brief
  Firefox UI check only for behavior the automated policy inspection cannot
  observe. Do not convert XPI contents into shell code.
- Require that deeper policy and user-data recovery evidence before a
  runnable status because this outcome controls browser security policy.

The standalone Python tool remains the **documented replacement interface**
for v3.0; its `--help` and module header describe direct commands and
backups.
There is no v3 catalog operation or `ride.sh apply` claim for it. The
existing [focused Python tests](../../tests/test_manage_firefox_extensions.py)
cover manifest validation and policy transitions, but no exact-target v3
engine/VM policy recovery has been accepted. Reopen catalog integration
when the journal and seeded-policy gate above passes. The replacement is
counted separately from runnable installs.
