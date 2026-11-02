# Plex Media Server Fedora 44 Server acceptance

Status: **passed**, 2026-11-02, Fedora 44 Server x86_64 under QEMU TCG.
VM acceptance result: **PASS**.
The test exercises `package.plex-server` and
`setting.plex-server-service` through the opt-in profile
`profiles/fedora-server-plex.json`.

The current official Plex RPM repository and PlexSign v2 key were used. The
catalog pins primary fingerprint
`6EFFEB478A6559D75C7C4FE706C521790B9CFFDE`; the repo file enables both
`gpgcheck=1` and `repo_gpgcheck=1`. DNF's first metadata lookup logged that the
signing key was not yet available. After fetching and importing the repository
key, the DNF log records `Signing key found` and `GPG signature successfully
verified` for `repomd.xml`; DNF then verified and installed
`plexmediaserver-1.43.5.11079-b3b13e506.x86_64`.

Before install, the disposable guest had a Plex account and a seeded
Plex-owned data tree containing marker bytes under `Metadata/` and
`Plug-in Support/Databases/`. Apply started and enabled the packaged service.
The test verified both marker hashes, the account UID/GID, service health,
repeat, status, restore, package and repository removal, and unchanged
firewalld state. Restore stopped and disabled Plex before removing the RPM;
both seeded markers and the account identity remained unchanged.

The first acceptance attempt exposed a fixture error: the seeded library's
ancestor directories were root-owned, so Plex could not create its Cache
directory. The journal identified the `Permission denied` path. The fixture
was corrected to give the entire seeded tree to the `plex` account, and the
full rerun passed. The run does not authenticate a Plex account, expose the
server through firewalld, or migrate a real library/database.

## Evidence

Successful run artifacts are in
`.acceptance-runs/generic-server-16-plex-server/`:

- `transcript.jsonl`, SHA-256
  `c33c45abf6021e49b96d555c351fd1c33ad3ae1b2b7b7abf9201239fe6fd5144`
- `dnf-signature-and-install.log`, SHA-256
  `7a0c441e27a1c33c7656aeef9d838c6530931df04f4669f3ed433d85bdc5fb36`
- `metadata.json`, SHA-256
  `080acdf1f05e89503db3e484a2b2ecf152dde4f6001b8cfa9613a4260b57087d`
- `serial.log`, SHA-256
  `5cc589273bc37731b59a1656e15e9ceeb34da192b204b6c26a4ace20b891f65e`

The QEMU log is empty. The test source is
[`test_plex_server.py`](../../tests/acceptance/test_plex_server.py).
