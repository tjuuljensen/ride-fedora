# BulkExtractor source build and forensic output

Status: **unsupported for v3.0**, 2026-10-30. This isolated high-risk batch
maps `InstallBulkExtractor` and `RemoveBulkExtractor`, both commented out of
the v2 preset. The installer clones an unpinned recursive Git tree into
`/opt`, changes its ACL, edits a Fedora configure helper, builds and runs
`make install` into `/usr/local`, and adds `edk2-tools-python`. Its inverse
deletes the clone and one guessed binary and removes a possibly shared RPM;
it does not track all installed files or forensic output.

## Completion criteria defined before a runnable operation

- Choose a tested upstream release artifact rather than a moving branch.
  Record its hash and notices, build in an owned workspace and prefix, and
  verify the actual binary and every installed file.
- Prove the inverse removes only owned program files and leaves evidence
  inputs, scanner output, and any pre-existing dependencies untouched.
  Include a seeded-data recovery test, a failed-build cleanup test, and a
  disposable Fedora 44 x86_64 Workstation lifecycle before support.
- Keep the source outcome visible with a specific reason and review trigger
  if the safety evidence is unavailable; a runnable candidate cannot waive
  the high-risk gate.

Current [upstream installation guidance](https://github.com/simsong/bulk_extractor/blob/main/INSTALL)
recommends a tested release archive, `make check`, and a chosen prefix.
Its [license statement](https://github.com/simsong/bulk_extractor/blob/main/COPYING)
identifies post-2015 project code as GPL-3.0-or-later with separately
licensed components. The v2 moving-branch build does not meet this contract,
and no v3 owned build, exact-target install, or seeded-data inverse exists.
This is a **non-runnable unsupported decision**, not a claim that upstream
BulkExtractor is unavailable. Reopen for a concrete forensic workflow with
the pinned build and recovery evidence above.
