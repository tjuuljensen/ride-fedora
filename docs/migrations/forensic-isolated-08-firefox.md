# Forensic Isolated 08: Firefox profile analysis successor

Status: **kept v3.0 capability; operable opt-in candidate passed Fedora 44
Workstation acceptance**, 2026-11-02. The v2 `InstallDumpzilla` downloads a discontinued,
mutable script to `/usr/local/bin`; its inverse removes that path without
checking ownership. The owner kept Firefox forensic analysis in scope. The
old script's retirement does not retire the capability.

## Completion checks defined before implementation

- Compare replacement coverage with Dumpzilla's history, cookies, downloads,
  bookmarks, forms, preferences, extensions, sessions, and login artifacts.
  Record unverified artifact types explicitly. Choose a licensed source with
  an immutable revision or exact artifact digest, locked dependencies, and an
  owned destination. Keep the tool opt-in.
- Installation and detection must not inspect Firefox profiles or reveal
  credentials. Restore and remove must preserve profiles, case inputs,
  reports, credentials, and unrelated files. Secret reveal must be a separate
  explicit CLI action with a caller-selected file and restrictive permissions.
- In a disposable Fedora 44 Workstation x86_64 VM, check plan, candidate gate,
  apply, repeat, status, restore, and explicit remove. Use a seeded synthetic
  Firefox profile containing history, a bookmark, and a cookie; compare input
  hashes before and after parsing. Exercise upstream synthetic login data,
  verify that plaintext does not reach stdout, and verify a secret file under
  `umask 077`. Focused mocked tests must reject bad source bytes, occupied
  destinations, failed build cleanup, and unowned removal.
- Record functional limits and exact target in the catalog, ledger, generated
  docs, Windows alignment, and acceptance record. Keep a v3.0 gap until the
  seeded-data and recovery evidence passes. Broader artifact coverage remains
  separately visible for hardening.

## Candidate comparison

| Candidate | Current evidence | Decision for this batch |
| --- | --- | --- |
| [Dumpzilla](https://github.com/Busindre/dumpzilla) | Upstream labels it discontinued; the v2 download was mutable and has no accepted current Firefox compatibility or owned inverse. | Retire this exact script path only; preserve its Firefox-analysis capability through a successor. |
| [browser-forensic](https://github.com/SecurityRonin/browser-forensic) | Apache-2.0. The current main/tag source revision is `10e2f70bd53d50144edcff849749efd0095c9a03`, not an obsolete pin. The source archive SHA-256 is `0493a03c0564a712a536fdd345c3eefec561c3ffd040f4ecc776ecdec398649c`; version `0.3.0` includes `Cargo.lock`. The CLI has Firefox artifact parsers and keeps decrypted passwords out of stdout. Its source writes the optional secret file using the process umask, so reveal must run under `umask 077`. | Selected as the pinned candidate. Build only the CLI; RIDE does not run analysis during apply. Leave opt-in pending Fedora 44 lifecycle and seeded-profile acceptance. |
| [Hindsight](https://github.com/obsidianforensics/hindsight) | The pinned `v2026.06` wheel and dependency set installed. Its synthetic Firefox fixture exported XLSX successfully without changing source files, while JSONL export failed on an upstream missing `expires_utc` field for a session cookie. Its documented Firefox subset does not establish extensions, sessions, preferences, and login parity. | Do not select for this batch: the JSONL failure and narrower artifact set make it a weaker current path. Retain as a possible future alternative if upstream fixes the export issue. |
| [Plaso](https://github.com/log2timeline/plaso/blob/main/docs/sources/user/Parsers-and-plugins.md) | Already a separate kept v2 outcome in `forensic-isolated-02`; it has Firefox timeline parsers. | Reuse its accepted path for timeline analysis, but do not count its subset as this complete profile-analysis capability. |

The acceptance run uses synthetic SQLite history, bookmarks, and cookies, then
the synthetic NSS credentials distributed with the pinned upstream source.
It does not use a real Firefox profile. `br4n6 artifact ...` commands are
read-only for these inputs; broader commands that reconstruct, export, or
checkpoint evidence are outside the v3.0 operation's install contract. Preserve
unverified Dumpzilla artifact parity in v3.1 review instead of claiming full
coverage from package installation alone.


## Fedora acceptance result

The pinned browser-forensic CLI and signed Cargo prerequisite passed the exact Fedora 44 Workstation x86_64 lifecycle. The VM verified candidate gating, locked release build, CLI version, synthetic history/bookmark/cookie parsing, unchanged Firefox database hashes, synthetic login secret isolation and 0600 output, repeat, status, active restore, reinstall, and explicit remove. The test completed 1/1 in 6740 seconds under TCG; the image digest, catalog digest, source bundle, and full transcript are recorded in [the acceptance record](../acceptance/package.browser-forensic.md). The operation is now an operable opt-in candidate. H116 keeps broader Dumpzilla artifact parity and real-profile review visible as v3.1 hardening.
