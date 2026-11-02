# WoeUSB 5.2.4 acceptance

`package.woeusb` is a Fedora 44 Workstation x86_64 opt-in candidate. It installs
upstream's standalone WoeUSB Bash 5.2.4 script under the user's private
`~/.local/opt/ride-fedora/woeusb/5.2.4` path and links it from
`~/.local/bin/woeusb`. The script and GPL-3.0-or-later license text are pinned
by SHA-256. The separate `fedora-woeusb-runtime` profile declares its Fedora
RPM requirements.

RIDE manages only the script's install lifecycle. Applying this operation does
not invoke WoeUSB with arguments, select a device, write a filesystem, or
create boot media. The disposable VM test checks package signatures and RPM
verification, command availability, plan, candidate gate, apply, script and
license digests, help/version, status, repeat, restore, remove, and preservation
of pre-existing runtime packages.

Completion evidence: `test_woeusb.py::test_woeusb_private_tool_lifecycle`
passed on 2026-11-01 against Fedora 44 Workstation x86_64, using TCG and image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Transcript:
`.tmp-vm-acceptance-publisher-apps-09-woeusb-final-2/fedora-44-workstation-x86_64/20261101T184213Z-test-woeusb-private-tool-lifecycle-10adf3d1/transcript.jsonl`
(SHA-256 `8586535e863c13f53a471477e2ef25769489a71a0e3ecbbc9cb6bde1946b0791`).
The checked catalog SHA-256 was
`f7da519847ff239f3a3cd6447f2ffa11f12c637c1b09d227c9bdd159a63429c9`.
Broader media compatibility and failure recovery remain v3.1 hardening.

The Fedora 44 Workstation x86_64 transcript covers these catalog IDs:
`package.woeusb`, `package.parted`, `package.dosfstools`,
`package.wimlib-utils`, `package.grub2-tools-extra`, `package.ntfs-3g`,
`package.ntfsprogs`, and `package.wget2-wget`.
