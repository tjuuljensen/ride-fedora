# Firefox add-on policy acceptance

Status: blocked; Fedora 44 Workstation x86_64 acceptance has not yet proved managed add-on installation.

## Completion checks

- Plan is read-only and the blocked operation requires explicit candidate
  evidence before mutation.
- Apply merges the manifest into Firefox `ExtensionSettings`, preserves seeded
  unrelated policy, and validates current add-on IDs and source hashes.
- Repeat is unchanged and status reports `configured`.
- Firefox startup installs every managed add-on in the seeded profile.
- Removal writes only managed IDs as `blocked`, reports `removal-pending`, and
  preserves unrelated policy and profile data.
- Restore from `removal-pending` returns to `configured` exactly.
- A second removal plus Firefox restart removes all managed add-ons, after
  which finalization removes only owned policy entries and the ownership record.

## Fedora 44 Workstation x86_64 result

The disposable VM applied the policy and passed the read-only plan, candidate
refusal, apply, repeat, and status checks. It preserved the unrelated
`Homepage` and extension policy entries. Firefox then started headlessly for
60 seconds, but its profile contained only five built-in add-ons; none of the
16 policy-managed AMO add-ons appeared in `extensions.json`. The run stopped
before removal/recovery. Transcript:

`.acceptance-runs/fedora-44-workstation-x86_64/20261102T105605Z-test-firefox-addon-policy-lifecycle-and-restart-recovery-6df05733/transcript.jsonl`

This is an investigated failure, not acceptance. Mozilla's current
[ExtensionSettings reference](https://firefox-admin-docs.mozilla.org/reference/policies/extensionsettings/)
documents the managed install URL form, and its
[policy setup guide](https://firefox-admin-docs.mozilla.org/guides/policies-configuration/)
documents `/etc/firefox/policies/policies.json` as the Linux policy path. This
VM result does not establish that Firefox fetched or installed the configured add-ons.
Do not retry the same policy/startup flow unchanged. Next, inspect the effective
policy and Firefox extension-install diagnostics on a disposable VM, then
adjust the installation path or preserve this as a non-runnable v3.0 gap until
it is proven.
