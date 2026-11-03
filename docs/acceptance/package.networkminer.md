# NetworkMiner Fedora 44 Workstation acceptance

Status: **passed as an opt-in candidate**, 2026-11-02.

The disposable Fedora 44 Workstation x86_64 run installed the Netresec 3.2
archive at the pinned SHA-256, `daceec649fb4fe59b11e4a9e4ecd5f51c1dd37824280dfbeac67bec27b6b6d60`.
The separate system profile installed Fedora `gtk2` 2.24.33-25.fc44 and Mono
6.14.1-4.fc44 (`mono-core`, `mono-winforms`) through Fedora's signed DNF
repositories. DNF installed and later removed the associated dependencies as
well. Removing the runtime profile left all three explicitly requested
packages absent.

The user profile passed plan, candidate gating, apply, complete journal,
status, repeat, restore, reinstall, and remove. The NetworkMiner launcher and
desktop link pointed into its owned user-local program directory; the bundled
`Fingerprints/mac-ages_LICENSE` notice was retained. GUI startup under Xvfb
remained alive until the expected 15-second timeout (exit 124). No capture was
opened and no network capture was started.

Seeded capture and assembled-output files survived both restore and profile
removal byte-for-byte:

- `Captures/seed.pcap`: SHA-256
  `930e9648e7055a1c4bc67a72873e496c105038ac9fe643e323a18739ddddcaee`
- `AssembledFiles/seed.txt`: SHA-256
  `c7a51f3e9b8b11532a99d027d135af5f588b5dd94da40e557b1967916acf8296`

Deep data review checks:

- `private-output-boundary`: output directory is user-owned mode 0700 and is outside the package inverse.
- `no-evidence-processing`: apply and GUI smoke did not open PCAP data or start capture.
- `exact-output-preservation`: both seeded output hashes remained identical after restore and removal.

Focused automated tests: `python3 -m unittest tests.test_v3_networkminer -v` (3 passed).
Disposable VM test: `tests/acceptance/test_networkminer.py`, 1 passed in 509.22 seconds using TCG.
Target image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

Transcript: `.acceptance-runs/networkminer-final/fedora-44-workstation-x86_64/20261102T155104Z-test-networkminer-user-program-and-output-data-lifecycle-c58a1123/transcript.jsonl`
Transcript SHA-256: `7f53a80474b7ee6ac724c8e4b52532ed783cedece565b71499f1746b940049d7`
Overlay SHA-256: `30597e437bd4937502f5566237e47e330554a14326c86dd758bc81d19fe1c806`
Metadata SHA-256: `34586397b1f5fbbfaba7f15c46cb847ae94735a82d90b777ceb52d6834e617ad`

The operation remains an explicit opt-in candidate. H110 covers later
authorized PCAP analysis, live capture, hostile-input isolation, output limits,
credential exposure, and broader evidence-data handling.

Acceptance scenario: [`test_networkminer.py`](../../tests/acceptance/test_networkminer.py).
