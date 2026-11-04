# `package.eza-portable` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

This is a user-scoped portable deployment, separate from the Fedora RPM
operation `package.eza`. It installs Eza 0.23.5 to
`~/.local/opt/ride-fedora/eza/0.23.5/eza`, exposes it at `~/.local/bin/eza`,
and records owned files in
`~/.local/share/ride-fedora/owned-tools/package.eza-portable.json`. The
operation verifies the pinned archive SHA-256 before reading the archive and
does not write to `/usr/bin` or mutate the RPM database.

The source is the [upstream 0.23.5 GNU x86_64 release asset](https://github.com/eza-community/eza/releases/download/v0.23.5/eza_x86_64-unknown-linux-gnu.tar.gz)
with SHA-256
`35c70c5c43c29108075e58b893234c67ef585f0b53a7eaf8e9e7d4eec9f339b4`. GitHub
shows the release tag signature as expired, so this evidence is a pinned
publisher digest check rather than a signature-verification claim. Upstream
declares EUPL-1.2 and links the versioned
[`LICENSE.txt`](https://raw.githubusercontent.com/eza-community/eza/v0.23.5/LICENSE.txt).

The focused disposable VM lifecycle passed candidate refusal, plan, versioned
user-local install alongside Fedora's signed `eza` RPM, version and status,
unchanged repeat, remove, unchanged RPM identity, and preserved sibling user
data. The portable executable was only invoked with `--version`; no host data
was listed.

VM evidence: Fedora 44 Workstation x86_64; pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`;
overlay `20261101T143112Z-test-eza-portable-pinned-user-install-coexists-with-fedora-rpm-640ef901`;
catalog SHA-256
`d76d51216b6ea4c647ff70b8ef51ac9b2a4da7aada440a66618729aa09cc33fc`;
transcript [transcript.jsonl](../../.acceptance-runs/legacy-vm/.tmp-vm-acceptance-provider-08-eza-portable/fedora-44-workstation-x86_64/20261101T143112Z-test-eza-portable-pinned-user-install-coexists-with-fedora-rpm-640ef901/transcript.jsonl)
SHA-256 `1c609e945ec30d205a484480031ed01a9435a14bcaac0049e155fbe82a255b8a`.
Run IDs: apply `20261101T143156Z-2699-22741`, repeat
`20261101T143158Z-3224-9275`, remove `20261101T143159Z-3444-12885`. Fedora's
RPM remained installed and unchanged throughout portable removal. Because the
RPM was absent at VM baseline, the acceptance test removed that temporary RPM
after coexistence verification.
