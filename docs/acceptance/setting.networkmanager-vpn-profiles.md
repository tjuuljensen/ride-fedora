# NetworkManager VPN profile acceptance

Operation `setting.networkmanager-vpn-profiles` **PASS**: supported on Fedora
44 Workstation x86_64, 2026-11-02. The lifecycle ran in a Fedora 44 Workstation
x86_64 disposable **VM**.

## Scenario

`tests/acceptance/test_networkmanager_vpn_profiles.py` seeded two inactive
synthetic system VPN keyfiles and one unrelated keyfile. It records content,
owner, group, mode, nanosecond modification time, and extended attributes.
The test checked plan, apply without `--allow-candidate`, repeat, status,
credential-marker exclusion from the run journal, run restore, and exact
restoration of all three keyfiles including content, ownership, mode,
nanosecond modification time, and extended attributes. It removed only the
synthetic fixtures after comparing their state. It did not activate a VPN
connection, contact a VPN endpoint, alter routes, or configure a VPN provider.
Mocked tests cover active-profile refusal, activation after snapshot,
partial-delete rollback, reload rollback, changed-file detection, and malformed
or duplicate UUIDs.

## Result

The scenario passed in a disposable Fedora 44 Workstation x86_64 VM with TCG
acceleration and pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

- Command: `PYTHONPATH=. pytest -q tests/acceptance/test_networkmanager_vpn_profiles.py --vm-target fedora-44-workstation-x86_64 --vm-pilot setting.networkmanager-vpn-profiles --vm-image .acceptance-runs/workstation-image-build/workstation.qcow2 --vm-accel tcg`
- Result: 1 passed in 173.31 seconds.
- Run ID: `20261102T172753Z-2511-31731`.
- Evidence directory: `.acceptance-runs/networkmanager-vpn-profiles/fedora-44-workstation-x86_64/20261102T172550Z-test-uuid-scoped-vpn-profile-lifecycle-and-exact-restore-7d838641/`.
- Transcript SHA-256: `8d486b48c63795b59654c4aeda86d2e09ac71ae3820c987a95ad1f8ec573a598`.
- VM metadata SHA-256: `c573fd49f045d962a1fe8df8304d1d1315d3c6b242fa51040eade8694fa062ab`.
- Overlay SHA-256: `9cba88344b0934297f73f38faf2b98133ad869202ae63e62e97ee40c5c72d6cc`.

The run journal contained the selected UUID value and no synthetic credential
markers. After restore, all three file-state records matched their pre-run
values. The catalog now marks the operation supported only on Fedora 44
Workstation x86_64; other editions, distributions, architectures, user
profiles, activation, and routing behavior remain unsupported.
