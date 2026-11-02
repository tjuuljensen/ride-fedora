# Desktop and user aliases migration

The kept v2 outcomes `EnableBashAliases`, `SetAliasLsEza`, and
`SetAliasWanIP` are migrated together as one user-scoped, opt-in Bash setting.
RIDE must source the user's existing `~/.bash_aliases` file through an owned
block in `~/.bashrc` and add only selected aliases through a separately marked
block in `~/.bash_aliases`. It must not replace either file. Removal removes
only unchanged RIDE blocks, preserves unrelated edits, and refuses missing,
duplicated, or edited ownership markers. A file created by RIDE is removed
only if it is empty after its owned block is removed.

The configurable alias selection is limited to `ls-eza`, `wanip`, `wanip4`,
and `wanip6`; command text is generated from a fixed table and never accepted
from profile data. `ls-eza` maps to the maintained Eza command and requires Eza
to be installed. WAN address aliases use ipify's documented HTTPS text
endpoints: `api64.ipify.org` for the route-selected address, `api.ipify.org`
for IPv4, and `api6.ipify.org` for IPv6. Calling these aliases makes an
explicit request to a public third-party service and requires network access.
The IPv6 endpoint can fail when IPv6 is unavailable. Source reviews:
[Eza installation](https://github.com/eza-community/eza/blob/main/INSTALL.md)
and [ipify API documentation](https://www.ipify.org/).
The [opt-in profile](../../profiles/fedora-shell-aliases.json) declares the
Fedora Eza and curl packages separately from this user setting.

## Completion checks before verification

- Catalog and profile validation reject unknown alias IDs and shell syntax
  supplied as values; the handler emits only fixed commands.
- Mocked tests seed existing `.bashrc` and `.bash_aliases` content, verify
  plan/apply/repeat/status/remove, preserve user edits outside owned markers,
  refuse alias-name conflicts and modified owned blocks, and exercise rollback
  after a partial file update.
- One Fedora 44 Workstation x86_64 disposable VM checks candidate gating,
  actual interactive Bash alias visibility, repeat, exact owned-block removal,
  and preservation of a user's later unrelated edits. It verifies the Eza
  alias resolves to an installed `eza`; it does not call the public IP service.
- Keep this capability opt-in. Use the single automated VM session as
  implementation evidence; no manual shell session is needed.

The Chrome preferences outcome stays separate. A current policy path is now
known: the Flathub wrapper imports host Chrome policy directories. The next
batch must map the retained first-run defaults to user-changeable recommended
policies where semantics match, while reviewing the security-reducing values
separately and preserving existing policy files.
