# YubiKey Manager GUI and current Yubico tools

The owner kept YubiKey management in v3.0. The v2 Manager GUI is end of life,
and the old mutable AppImage install and name-based remove path is not reusable.
Yubico's current GUI successor is Yubico Authenticator; Yubico continues the
`ykman` CLI as a separate tool.

Status: **CLI supported; GUI is an operable opt-in candidate**, 2026-11-01. This high-risk active-preset outcome maps
`InstallYubikeyManager` / `RemoveYubikeyManager`.

## Source and deployment review

Fedora 44 provides a Fedora-signed `yubikey-manager` package with the `ykman`
CLI. Fedora reports version 5.9.2 and the upstream project uses BSD-2-Clause.
The operation [`package.yubikey-manager`](../acceptance/package.yubikey-manager.md)
installs or removes that RPM only. The opt-in `fedora-yubikey-tools` profile
does not configure a key or enable `pcscd`.

Yubico publishes a Linux tarball for Yubico Authenticator 7.4.1, alongside an
OpenPGP signature, and documents extracting that tarball as its Linux install
method. The official release archive is 60,685,155 bytes and its observed
SHA-256 is `5c8f49cf3653ae9dd3911b53ca60475b03c8c957eb7385b1bd3d49ec4767ddac`.
The digest was independently matched against the official download. Yubico's
software signing page publishes developer key fingerprints for signature
verification. The source repository is Apache-2.0.

- [Yubico Authenticator releases and signatures](https://developers.yubico.com/yubioath-flutter/Releases/)
- [Linux installation instructions](https://docs.yubico.com/software/yubikey/tools/authenticator/auth-guide/installation.html)
- [Yubico software-signing guidance](https://developers.yubico.com/Software_Projects/Software_Signing.html)
- [Yubico Authenticator source and license](https://github.com/Yubico/yubioath-flutter)
- [Fedora 44 ykman package](https://packages.fedoraproject.org/pkgs/yubikey-manager/yubikey-manager/)

## Completion checks defined before GUI implementation

- Add an opt-in user-scoped GUI deployment from the pinned official tarball.
  Extract without running upstream install scripts, own the versioned app tree,
  launcher, desktop entry, and icon, and refuse collisions with existing files.
- Record exact ownership so remove deletes only files installed by RIDE. Preserve
  pre-existing Authenticator preferences, other `~/Applications` content, and
  unrelated desktop entries. Verify the archive digest before extraction and
  reject unsafe archive members.
- On the declared Fedora 44 x86_64 Workstation VM, check absent plan, apply,
  repeat, status, exact executable and launcher paths, and exact removal. Seed
  synthetic existing preferences and verify they are byte-identical. Do not
  attach a YubiKey or perform credential operations.
- Keep the existing Fedora `ykman` RPM as its own operation so CLI and GUI
  deployments can be selected independently. Any key configuration behavior
  remains user initiated and outside RIDE package lifecycle management.

The `ykman` RPM lifecycle passed on the pinned Fedora 44 Workstation image and
is supported for package presence. The Authenticator archive lifecycle also
passed on Fedora 44 Workstation: the VM verified the publisher signature and
pinned digest, installed the owned tree and launch paths, repeated apply,
reported status, removed only owned paths, and preserved seeded preferences and
unrelated `~/Applications` data. Both owner-kept source outcomes are now
**operable opt-in candidates**, mapped to `package.yubikey-manager` and
`package.yubico-authenticator`. Neither profile is in a base profile.

The migration risk is medium because RIDE only manages software files and
launchers; it does not communicate with or configure a key. The GUI was not
launched in the headless acceptance VM. H072 tracks optional GUI and device
visibility checks; any future RIDE-managed credential or key configuration
must be a separate high-risk operation.
