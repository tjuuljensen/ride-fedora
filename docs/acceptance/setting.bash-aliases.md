# User Bash aliases acceptance

`setting.bash-aliases` is an opt-in Fedora 44 Workstation x86_64 setting for
the kept v2 `EnableBashAliases`, `SetAliasLsEza`, and `SetAliasWanIP` outcomes.
It uses fixed alias templates and exact marked blocks in the user's
`~/.bashrc` and `~/.bash_aliases`. Apply, status, and removal never source
catalog or profile data. Existing shell content and later unrelated edits are
preserved; modified RIDE blocks stop removal. The Eza alias requires the Eza
command. WAN aliases use ipify's HTTPS endpoint and make a public network
request only when the user runs the alias.

Mocked tests cover configuration validation, apply, repeat, status, exact
owned-block removal, seeded and later user-content preservation, alias-name
conflicts, refusal after an external edit, and rollback when the loader update
fails. They also verify that profile values cannot inject shell syntax.

Fedora 44 Workstation x86_64 disposable-VM acceptance passed plan,
candidate-gating, apply, journal value, interactive alias visibility, Eza
execution, status, repeat, and removal while preserving later user edits. The
WAN aliases were inspected but not invoked, so this run made no request to the
public ipify service. Transcript:
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-desktop-user-05-aliases/fedora-44-workstation-x86_64/20261101T222729Z-test-bash-aliases-interactive-lifecycle-and-user-content-c0a1009e/transcript.jsonl`
(SHA-256
`001205de18a44337b3237ee061237f57a05bcf429d0bad03dd57641eb189033a`); image
SHA-256:
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

Keep this operation opt-in and outside base profiles. H090 tracks review of the
public IP service choice and privacy behavior before promoting or broadening
the alias capability.
