# Forensic Isolated 08: Firefox profile analysis successor

Status: **kept v3.0 capability, successor selection pending VM evidence**,
2026-10-30. The v2 `InstallDumpzilla` downloads an unpinned discontinued
script to `/usr/local/bin`; its inverse removes that path without checking
ownership. The owner kept Firefox forensic parsing in scope. Retirement of
the old script does not retire that capability.

## Completion checks defined before implementation

- Compare replacement coverage with Dumpzilla's history, cookies, downloads,
  bookmarks, forms, preferences, extensions, sessions, and login artifacts.
  Record unsupported artifact types explicitly. Choose a current licensed
  source with fixed version or commit, locked dependencies or an exact
  artifact digest, and an owned destination. Keep this operation opt-in.
- The installer must not scan browser profiles or reveal credentials.
  Detection must identify only the owned tool. Restore and remove must
  preserve Firefox profiles, case inputs, generated reports, credentials,
  and unrelated files. A product that can reveal secrets must require an
  explicit separate user command and output destination; apply cannot
  enable decryption or export.
- In a disposable Fedora 44 Workstation x86_64 VM, test plan, opt-in gate,
  apply, repeat, status, restore, and explicit remove. Use a seeded
  disposable Firefox profile with representative history and another
  artifact type; compare input hashes before and after read-only parsing.
  Test secret output isolation separately with synthetic credentials if
  the selected tool supports it. Focused mocked tests must reject bad
  source bytes, occupied destinations, failed build cleanup, and unowned
  removal. A `--help` result alone is insufficient.
- Record the replacement's functional limits and exact target in the
  catalog, ledger, generated docs, Windows alignment, and acceptance record.
  Retain a v3.0 gap until the seeded-data and recovery evidence passes.
  Broader browsers and artifact coverage may move to v3.1 after this gate.

## Candidate comparison

| Candidate | Current evidence | Decision for this batch |
| --- | --- | --- |
| [Dumpzilla](https://github.com/Busindre/dumpzilla) | Upstream labels it discontinued; the v2 download was mutable and no current Firefox compatibility or owned inverse was accepted. | Retire this exact script path only. |
| [browser-forensic](https://github.com/SecurityRonin/browser-forensic) | Apache-2.0 source at commit `10e2f70bd53d50144edcff849749efd0095c9a03`, covering Firefox history, cookies, downloads, bookmarks, autofill, extensions, sessions, login metadata, and preferences. Its README says evidence is opened read-only and secret reveal requires explicit flags and file output. The repository has a lockfile and Linux CI but no published GitHub release. | Primary source-build candidate; pin source and Cargo dependencies, then check its actual CLI and seeded-data behavior in the declared VM. No runnable claim yet. |
| [Plaso](https://github.com/log2timeline/plaso/blob/main/docs/sources/user/Parsers-and-plugins.md) | Maintained Firefox history, cookies, downloads, and cache parsers. Plaso is already a separate kept v2 outcome in `forensic-isolated-02`. | Reuse its future accepted path for timeline analysis, but do not silently treat that subset as complete Dumpzilla coverage. |

The browser-forensic README documents optional password output, so this
batch is high risk even though RIDE would install the tool without reading
profiles. A source build is a development path, not accepted installation
evidence. The next action is a pinned Fedora 44 build and synthetic-profile
probe, followed by an owned v3 operation only if those checks pass.
