# DNF5 FastDNF tuning acceptance

Status: **PASS for the Fedora 44 Workstation x86_64 target; operation remains opt-in candidate**.

Acceptance run: `tests/acceptance/test_dnf5_fast_tuning.py` passed on 2026-11-02
using the pinned `fedora-44-workstation-x86_64` target and TCG acceleration.
Transcript: `.tmp-vm-acceptance-system-security-01-fastdnf-fixed/fedora-44-workstation-x86_64/20261102T001931Z-test-owned-dnf5-tuning-profile-applies-repeats-and-restores-0db652ff/transcript.jsonl`
SHA-256: `595f0fa1a0302f0e761851cabf187330ffee1ef60127e0d07bc9e17993dbd5c5`.
Image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

## Declared behavior

- Target: Fedora 44 Workstation x86_64.
- Operation: `setting.dnf5-fast-tuning`.
- Profile: `fedora-fast-dnf` (opt-in; not part of `default`).
- Apply: create `/etc/dnf/libdnf5.conf.d/99-ride-fastdnf.conf` with
  `fastestmirror=True` and `max_parallel_downloads=15`.
- Repeat: observe the exact RIDE-owned file and leave it unchanged.
- Restore: remove only that exact file when the journal says it was absent.
- Conflict behavior: refuse an existing unowned RIDE path, competing values in
  DNF configuration files, missing DNF5 configuration directories, or effective
  values that do not match the requested state.

## Automated evidence

`tests/test_v3_dnf5_fast_tuning.py` covers apply, repeat, exact absence restore,
unowned file refusal, administrator config refusal, and competing drop-in
refusal. `tests/acceptance/test_dnf5_fast_tuning.py` exercised the lifecycle against the
pinned Fedora 44 Workstation image. The run confirmed DNF5 effective values,
repeat behavior, and exact removal of the previously absent drop-in. The
operation remains opt-in candidate; H093 tracks future DNF5 precedence review.
