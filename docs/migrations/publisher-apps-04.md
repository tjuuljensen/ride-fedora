# Publisher Apps 04: Firefox extension policy

Status: **v3 envelope implemented but blocked; Fedora 44 acceptance pending**,
2026-11-02. The owner kept v3-managed Firefox add-on policy capability. The
existing standalone tool is now called through `setting.firefox-addons` and
the opt-in `fedora-firefox-addons` profile. The catalog marks it `blocked` until
the policy, browser restart, profile cleanup, and restoration checks below
pass. The candidate override cannot bypass this gate.
This isolated active-preset outcome maps `InstallFirefoxAddons` and
`RemoveFirefoxAddons`. The current v2 functions already delegate to the
repository's maintained [`manage-firefox-extensions.py`](../../tools/manage-firefox-extensions.py).
That tool validates a manifest, checks Mozilla Add-ons and XPI IDs before
install, merges `ExtensionSettings` into `/etc/firefox/policies/policies.json`,
backs up prior policy, and records ownership. Removal writes blocked
tombstones for Firefox to process; a separate finalizer removes them.

## Completion criteria defined before a runnable v3 operation

- Represent the exact manifest and policy ownership in the v3 catalog and
  run journal. Observe `configured`, `removal-pending`, and `absent` as distinct
  states. Refuse conflicts with unrelated administrator policy.
- On `configured -> absent`, write Mozilla's `blocked` entries and journal a
  pending restart. Do not report absence until Firefox has restarted, all
  discovered profiles no longer contain the managed extension IDs, no Firefox
  process is running, and the policy tombstones can be removed safely.
- Test AMO acquisition failure, interrupted writes, modified-policy refusal,
  restoration from the pending state, and preservation of seeded administrator
  policy and browser profile data.
- Run the full lifecycle on disposable Fedora 44 x86_64 Workstation. One
  automated headless startup checks that Firefox consumes policy and removes
  the extensions; reserve a brief manual session only if the declared behavior
  cannot be observed through profile and policy state.
- Keep this security-policy operation non-runnable until the deep ownership
  and recovery evidence is established. XPI data is never evaluated as code.

The Python helper remains the policy implementation. The v3 handler now calls
its `observe` and `set-state` interface and keeps the complete Firefox restart
boundary inside the catalog state machine. Focused Python tests cover policy
ownership and phases; exact-target engine and browser recovery remains pending.

## v3 lifecycle design constraint

This policy has three meaningful states: configured, removal pending, and
absent. The catalog now exposes each state. When a configured-to-absent change
first writes Mozilla's `blocked` entries, RIDE journals the observed
`removal-pending` state and marks the run pending. The operator restarts
Firefox, then reapplies the absent profile state; the finalizer verifies that
Firefox is stopped and the managed IDs have left discovered Firefox profiles
before it removes only the owned tombstones. Restore from a pending state
returns the managed policy to configured. Unrelated administrator policy and
profile content remain outside RIDE ownership.

The opt-in profile is not runnable while the catalog operation is blocked. The
catalog may move to candidate only after focused Fedora 44 Workstation
acceptance proves the policy and profile recovery behavior; candidate status
then remains explicit opt-in.
