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
| [browser-forensic](https://github.com/SecurityRonin/browser-forensic) | Apache-2.0 source; the earlier proposed commit `10e2f70bd53d50144edcff849749efd0095c9a03` is an old pin. The repository has no published GitHub release. Its current README describes broad Firefox artifact coverage, read-only SQLite access, and a separate secret-reveal command. | Do not build from the stale proposed pin. Re-evaluate only after recording a current immutable source revision and checking its current CLI and build inputs. |
| [Hindsight](https://github.com/obsidianforensics/hindsight) | Released Firefox support in `v2026.06` (signed release commit `25bfb16`). The official README documents Firefox history, bookmarks, downloads, cookies, and form history, with JSONL, XLSX, or SQLite output. Its tagged requirements still include an unpinned `ccl_chromium_reader` Git dependency. The documented Firefox subset does not establish Dumpzilla parity for extensions, sessions, preferences, or login artifacts. | Better released candidate for a narrower first path. Pin and verify the wheel plus every transitive dependency, then probe synthetic profiles and secret behavior before deciding whether it can serve as the opt-in v3.0 successor. |
| [Plaso](https://github.com/log2timeline/plaso/blob/main/docs/sources/user/Parsers-and-plugins.md) | Maintained Firefox history, cookies, downloads, and cache parsers. Plaso is already a separate kept v2 outcome in `forensic-isolated-02`. | Reuse its future accepted path for timeline analysis, but do not silently treat that subset as complete Dumpzilla coverage. |

Both candidates remain investigation inputs, not accepted installation
evidence. Hindsight currently has the clearer released Firefox path but needs
its Git dependency pinned and its actual profile-read behavior checked. The
next action is to pin a complete dependency set and run a synthetic-profile
probe in the disposable Fedora 44 target; proceed to an owned opt-in operation
only if read-only input and secret-handling checks pass. Keep the remaining
Dumpzilla artifact gaps explicit if the first v3 path covers only the Hindsight
Firefox subset.
