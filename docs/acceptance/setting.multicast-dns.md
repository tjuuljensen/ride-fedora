# MulticastDNS authselect acceptance

`setting.multicast-dns` is an opt-in Fedora 44 Workstation x86_64 candidate.
It controls authselect's `with-mdns4` feature and journals the exact selected
profile and feature list. It refuses unmanaged or invalid authselect state,
profiles without the feature, non-terminal `with-mdns4` selections, and
profile changes made outside RIDE. The generated `/etc/nsswitch.conf` is never
edited directly.

The Fedora package record describes `nss-mdns` as the glibc plugin for `.local`
name resolution and lists LGPL-2.1-or-later. Fedora's current authselect
profiles expose `with-mdns4`; the selected Fedora 44 Workstation image uses a
valid `local` profile with `with-silent-lastlog with-mdns4`. Sources:
[Fedora nss-mdns package](https://packages.fedoraproject.org/pkgs/nss-mdns/nss-mdns/),
[Fedora authselect package-maintainer notes](https://fedoraproject.org/wiki/User:Pbrezina/Authselect_and_packages_that_modifies_nsswitch),
[authselect feature and profile commands](https://github.com/authselect/authselect/blob/master/src/man/authselect.8.adoc).

## Completion checks

- Confirm the declared Workstation target has a valid authselect selection and
  `with-mdns4` is active before applying the opt-in profile.
- Check plan, candidate gate, apply, repeat, status, and exact restore.
- Confirm `authselect check` succeeds, the active `hosts:` line preserves
  `files`, `resolve`, and `dns`, and `getent hosts localhost` works while
  `mdns4_minimal` is absent.
- Change an unrelated authselect feature after apply. RIDE must refuse restore
  until that external change is reversed; then restore the original profile
  selection and resolver line byte-for-byte.
- This isolated VM has no mDNS peer, so it does not claim discovery of another
  `.local` host. H100 covers profile compatibility and broader behavior.

The mocked tests exercise idempotence, invalid authselect refusal, feature
selection ownership, external profile edits, and exact restoration.

Disposable VM run: **PASS**, Fedora 44 Workstation x86_64, QEMU TCG. The
declared image SHA-256 is
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`. The run
verified the candidate gate, apply, repeat, status, `authselect check`, local
hostname lookup, resolver ordering, refusal after an external authselect
feature change, and exact restoration of the profile selection and `hosts:`
line. It did not test discovery of a separate mDNS peer.

The first lifecycle attempt stopped at the final restore because the test
omitted the required `--allow-candidate` flag. The corrected test passed from
a fresh overlay; no source change was needed for the handler.

- Transcript: [`transcript.jsonl`](../../.acceptance-runs/system-security-06-multicast-dns/transcript.jsonl)
- Transcript SHA-256: `0b7d2d9867958872220165a68e88b13679cdfc2a83431c134387830811618038`
- VM metadata: [`metadata.json`](../../.acceptance-runs/system-security-06-multicast-dns/metadata.json)
- Source bundle SHA-256: `7c0589b8f5c7438cbb6872319e810e3af681fec840790c5b17f448adb5939654`
