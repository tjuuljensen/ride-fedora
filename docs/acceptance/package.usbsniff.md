# `package.usbsniff` acceptance

Status: **CANDIDATE LIFECYCLE PASSED** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora ships the signed `usbsniff` RPM (version `0-26.20170624gitb4ba3c8.fc44`)
under GPL-3.0-or-later. See the [Fedora package page](https://packages.fedoraproject.org/pkgs/usbsniff/usbsniff/)
and [upstream repository](https://github.com/vdudouyt/usbsniff).

The candidate operation manages RPM presence only. The opt-in profile does not
invoke USB commands, load `usbmon`, capture/replay traffic, detach/reset a
device, or read host USB data. The device-level behavior remains intentionally
outside this package lifecycle acceptance.

The pinned Fedora 44 Workstation lifecycle passed candidate refusal, plan,
repository signature, `rpm -V`, four installed executables, status, repeat,
restore, explicit install/remove, scriptlet, file-capability, systemd-unit,
and exact package inventory checks. The transaction installed only the RPM.
No USB command was invoked and no device was connected.

Evidence: apply `20261101T140757Z-2572-11324`, repeat
`20261101T140809Z-3593-18052`, restore `20261101T140810Z-4029-10309`, explicit
install `20261101T140813Z-4633-13494`, and remove
`20261101T140816Z-4904-21166`. Transcript:
`../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ap/fedora-44-workstation-x86_64/20261101T140728Z-test-package-apply-repeat-status-restore-and-remove-9c5a8607/transcript.jsonl`
(SHA-256 `ce15cc22cf106e858768b21f0a70aa8b0edb5695af93c57f7c4e8221262a5e47`).
