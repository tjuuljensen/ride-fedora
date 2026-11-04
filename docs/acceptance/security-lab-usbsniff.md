# Security Lab USB capture/replay package acceptance

Status: **CANDIDATE LIFECYCLE PASSED** on Fedora 44 Workstation x86_64,
2026-11-01.

Batch 06AP maps the `usbsniff` package group member to
`package.usbsniff`. v3 manages Fedora RPM presence only. USB capture, replay,
driver detach, reset, `usbmon`, and any hardware access are excluded from the
operation and profile. Upstream documents that replay detaches the kernel
driver, which can interrupt a device until it is reconnected.

The opt-in profile contains only `package.usbsniff`. The pinned VM pilot will
check install lifecycle, RPM signature and files, the `usb_capture`,
`usb_replay`, `usb_detach`, and `usb_reset` executables, scriptlets,
capabilities, units, and package recovery. The transaction installed only the
RPM, and the exact RPM inventory returned to baseline after restore and
explicit removal. No USB device was connected or operated during acceptance;
none of the four executables was run.

Transcript: `../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-security-06ap/fedora-44-workstation-x86_64/20261101T140728Z-test-package-apply-repeat-status-restore-and-remove-9c5a8607/transcript.jsonl`
(SHA-256 `ce15cc22cf106e858768b21f0a70aa8b0edb5695af93c57f7c4e8221262a5e47`).
