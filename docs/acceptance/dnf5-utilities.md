# DNFutils replacement evidence

The v2 `dnf-utils` package outcome is replaced by Fedora 44 Workstation's
DNF5 and DNF5 plugins. The declared target already provides these commands,
so v3 does not install the obsolete DNF4 bundle or edit repository
configuration to make its old utilities available.

## Target evidence

In the disposable Fedora 44 Workstation x86_64 run
`20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85`,
the read-only checks passed before package changes:

- `rpm -q dnf5 dnf5-plugins`
- `dnf5 config-manager --help`
- `dnf5 download --help`

The captured command transcript is under
`.acceptance-runs/full-v2-migration/fedora-44-workstation-x86_64/20261030T113742Z-test-provider-kernel-and-python-packages-batch-79fd1c85/transcript.jsonl`.
The observed `config-manager` exposes repository management commands, and
`download` exposes package download options. This establishes the replacement
on the declared target; it does not claim that every DNF4 plugin feature has
an equivalent DNF5 command.

Reopen if the Fedora target loses either required command or the v3 provider
stops using the current DNF behavior.
