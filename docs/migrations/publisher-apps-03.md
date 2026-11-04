# VS Code and Brave publisher repositories

Status: **operable opt-in candidates accepted on Fedora 44 Workstation**,
2026-11-01. This related active-preset batch preserves
`InstallVisualStudioCode` / `RemoveVisualStudioCode` and
`InstallBrave` / `RemoveBrave` as separate product outcomes. Both v2
installers add a publisher repository and an RPM. VS Code's inverse also
removes a hard-coded global GPG key ID, which may be shared; Brave's inverse
leaves its repository behind. The owner kept both products for v3.0.

## Completion criteria defined before implementation

- Bind each product to its publisher's current Fedora repository, key,
  package identity, license, and Fedora 44 x86_64 target. Enforce package
  signature checks, validate the published key where a stable fingerprint is
  available, and prevent replacing an unowned repository file.
- A v3 handler must detect the installed package and repository separately,
  record which repository state it created, preserve existing package and
  user data, and remove only its owned package and repo file. Mock conflicts
  and failure cleanup. A disposable Fedora 44 Workstation VM must pass plan,
  apply, repeat, status, removal, signed RPM inspection, and a startup probe.
- Treat publisher keys retained in the system RPM database as persistent
  trust anchors. Never delete a global key solely by product key ID.
- Defer broader desktop and update behavior to v3.1; keep both applications
  out of base profiles.

[Microsoft's Linux instructions](https://code.visualstudio.com/docs/setup/linux)
publish a Fedora/RHEL `code` RPM repository and signing key. Microsoft Learn
publishes a 2025 repository key fingerprint
`BC528686B50D79E339D3721CEB3E94ADBE1229CF`. The live
[`config.repo`](https://packages.microsoft.com/yumrepos/vscode/config.repo)
currently sets both `gpgcheck=0` and `repo_gpgcheck=0`, despite the install
instructions showing package signature checking. RIDE must not copy that
weaker live config: use an owned repo definition with package `gpgcheck=1`,
pin the Microsoft key fingerprint, and keep metadata checking disabled unless
Microsoft provides verifiable metadata-signature evidence.

[Brave's Fedora 41+ instructions](https://brave.com/linux/) direct Fedora 44
to its DNF5 repository. The current
[`brave-browser.repo`](https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo)
sets `gpgcheck=1` and points to Brave's current Linux release signing key.
Brave explicitly says its Flatpak has unresolved sandbox differences and
recommends the publisher RPM when available, so the native repo is the chosen
path. The publisher's signing-key page publishes multiple release keys to
support rotation; RIDE should let DNF validate package signatures and preserve
imported trust keys rather than deleting a global key by product key ID.

Implement one owned repository-state operation per publisher and bind each
package operation to its exact DNF repo ID. Remove only repo files RIDE created
and still recognizes; never overwrite a pre-existing file. Package removal
must happen independently of repository cleanup. DNF may retain the trusted
publisher key in the RPM database; document that as a system trust anchor,
not as a fully reversible product-owned file. Mocked conflict and cleanup
tests passed. The Fedora 44 Workstation VM acceptance passed plan, candidate
gate, signed RPM installs, repeat, status through lifecycle reconciliation,
removal, startup probes, exact repository cleanup, and seeded user-data
preservation. DNF's `--from-repo` pins the requested package to the publisher
while allowing dependencies from Fedora; the earlier `--repo` restriction
blocked those valid dependencies and was corrected before the passing run.
Windows has a
separately accepted VS Code **user setup** deployment, which shares product
identity but not the Fedora system RPM installer or recovery.

Transcript: [transcript.jsonl](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-03-from-repo-retry/fedora-44-workstation-x86_64/20261101T161819Z-test-publisher-repository-rpm-lifecycle-and-user-profile-recovery-92c61583/transcript.jsonl)
(SHA-256 `6084265f71cc0fd5db3926a0cc5a01921d4c85fe3428cc84e07576caa2696cb7`)
on Fedora 44 Workstation x86_64 image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Broader desktop/update checks remain v3.1 work.
