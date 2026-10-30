# RIDE v3 commands

Generated from `ride.sh --help`.

```text
RIDE Linux 3.0.0 - explicit, catalog-driven setup

Usage: ./ride.sh <command> [argument] [options]
  list [all|packages|artifacts|settings|profiles|groups]
  search <literal query>
  show <operation-id> [--source source-id]
  plan [--profile name-or-path]
  apply [--profile name-or-path]
  download <package-or-artifact-id> [--source source-id] [--destination directory]
  install <package-id> [--source source-id]
  set <setting-id> --state <declared-state>
  unset <setting-id>
  status [operation-id] [--source source-id] [--profile name-or-path]
  restore --run-id <id>
  remove <package-id> [--source source-id] | remove --profile name-or-path
  completion bash

Options: --dry-run previews state-changing commands; --allow-candidate enables
development-only operations without VM acceptance. System changes need sudo.
No command defaults to list. Profiles and catalog are JSON data, never shell.
Package source selection is explicit; profiles may declare a source per package.
Download does not install. Installing from a retained local artifact is pending.
Interactive tables use column when available; redirected output remains TSV.
```
