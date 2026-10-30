# Forensic Isolated 01 follow-up: ASN lookup tool

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**,
2026-10-30. The v2 `InstallASN` installs ten shared Fedora tools, downloads
the mutable upstream Bash script to `/usr/bin/asn`, and its inverse removes
some shared packages without checking their prior state. The v3 path uses a
fixed upstream commit, an owned user script and command link, and separately
selected Fedora RPM prerequisites. It does not enable ASN's optional server,
grant network capabilities, or alter `.asnrc` or lookup data.

## Completion checks defined before implementation

- Pin `nitefood/asn` commit
  `9384c07a35f5689ab7730c88b391ec47a8f2a11e`; require SHA-256
  `dee866df4d5d8ea26784611512d5dc962a1a6dbe33cbb20d9d23e7b492378d75`
  for its script and
  `7ba6dff361f2da0b9712fcc13960ba3d04d85cb9d073c97c5367241fdc2c8868`
  for its MIT notice. Download over HTTPS into a temporary owned path,
  verify before publication, and refuse an existing script, marker, or
  `~/.local/bin/asn` link. Do not source or execute the downloaded script
  during apply.
- Keep the ten upstream Fedora prerequisites as independent RPM operations:
  curl, whois, bind-utils, mtr, jq, nmap, nmap-ncat, ipcalc, aha, grepcidr.
  Reuse the existing `package.nmap` row. A system `asn-runtime` profile
  installs these; a user `asn-tool` profile installs only the pinned script
  after dependencies are observed. Each profile has its own run journal.
  Restore the system run to retain pre-existing RPMs; explicit removal of
  the user script must preserve user data.
- Mock failed download, bad digest, existing destination, and unowned removal
  without touching real user state. In one disposable pinned Fedora 44
  Workstation x86_64 VM, check both profiles' plan, apply, repeat, status,
  package signatures/files, ASN help startup, user command link, both
  profile restores, and explicit script removal. Compare pre-existing RPM
  identities and user files after recovery; investigate a failed run before
  retrying.
- After the focused VM happy path, add exact-target evidence and count an
  opt-in `candidate` as operable. Broader live lookups, server mode, and
  network failure handling remain v3.1. Keep `default` unchanged and update
  the ledger, generated docs, and Windows alignment.

Upstream [documents Fedora prerequisites and the script install](https://github.com/nitefood/asn#installation),
and publishes an [MIT license](https://github.com/nitefood/asn/blob/master/LICENSE).
The pinned commit and hashes bind the bytes actually acquired; the SHA-256
observations are not an independent publisher signature.

## Result

The [focused disposable VM run](../acceptance/package.asn.md) passed both
opt-in profiles, the script's exact hashes and help startup, the user inverse,
and system restore of newly installed package names. The first run exposed
only a test assertion error about ASN writing help to stderr; the corrected
test passed without an operational handler change. The DNF transaction
upgraded pre-existing `nmap-ncat` while installing `nmap`, and `ipcalc`
pulled weak GeoLite dependencies. These wider update and residue effects
remain H008; this candidate does not claim exact prior RPM versions.
