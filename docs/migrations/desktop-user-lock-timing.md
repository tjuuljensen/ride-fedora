# GNOME idle and automatic lock timing

## Completion checks

- Carry both retained v2 variants through one optional setting value: idle at
  600 or 900 seconds, enable idle activation and automatic lock, then lock 300
  seconds after activation. Do not permit a value that disables automatic lock.
- Validate each GNOME key's schema type and writability before mutation; fail
  closed when a key is system-locked or its schema differs from Fedora 44.
- Capture all four exact user dconf overrides, including whether each was
  unset. Treat the writes as one transaction: restore the complete snapshot
  after any failed write or post-write verification mismatch.
- Mock both retained values, repeat behavior, malformed journal rejection,
  partial-write rollback, and exact restoration.
- On Fedora 44 Workstation, seed four different user values, apply and repeat
  each profile, verify the four effective values and that locking remains
  enabled, then use RIDE `restore` and verify all seeded values exactly.
- Keep the profiles opt-in. Do not wait for the full idle timeout in the VM;
  schedule a brief visual idle/lock behavior check in H092.

## Mapping and safety

`SetScreensaverSlp10Lgn5` and `SetScreensaverSlp15Lgn5` both set
`org.gnome.desktop.session idle-delay`, enable
`org.gnome.desktop.screensaver idle-activation-enabled` and `lock-enabled`,
and set `lock-delay` to 300 seconds. The only difference is the 600- or
900-second idle delay. GNOME documents `idle-delay` as the inactivity period
before the session is idle, and `lock-delay` as the interval after screen saver
activation before the screen locks ([GNOME lock-screen administration](https://help.gnome.org/system-admin-guide/desktop-lockscreen.html)).

[`setting.gnome-lock-timing`](../../catalog/operations.json) accepts only the
`idle-10-lock-5` and `idle-15-lock-5` selections. The owned handler captures
all four raw dconf user overrides in the run journal and restores those exact
values. `absent` resets the four keys to their current defaults; `restore`
returns the pre-apply state. The operation always enables automatic screen
locking when configured and never invokes an immediate lock command.

The [10/5 profile](../../profiles/fedora-screen-lock-10-5.json) and
[15/5 profile](../../profiles/fedora-screen-lock-15-5.json) remain opt-in and
are not added to `default`. H092 tracks a brief visible check of idle activation
and lock behavior.

## Evidence

Automated partial-failure and exact-state recovery tests are in
[`test_v3_gnome_lock_timing.py`](../../tests/test_v3_gnome_lock_timing.py).
Fedora 44 Workstation VM evidence: pending.
