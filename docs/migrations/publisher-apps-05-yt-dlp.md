# Publisher Apps 05 follow-up: maintained video downloader

Status: **Fedora 44 Workstation VM passed; supported opt-in alternative**,
2026-10-30. The v2 `InstallYouTubeDownloader` and `RemoveYouTubeDownloader`
functions install and remove the `youtube-dl` RPM. Its existing v3 operation
and acceptance remain valid. This follow-up adds a distinct, maintained CLI
option for the same user intent; it does not replace a published operation ID.

## Completion checks defined before implementation

- Use Fedora 44's signed `yt-dlp` RPM, with the Fedora package record as source
  and license evidence. Declare only Workstation x86_64 until that exact
  target passes. Keep `package.yt-dlp` and `package.youtube-dl` separate:
  binaries and RPM identities must remain individually observable and removable.
- Reuse the unchanged DNF handler's mocked failure and journal evidence. In
  one disposable pinned Workstation VM, check absent plan, apply, signed RPM
  and files, `yt-dlp --version`, installed status, unchanged repeat, restore,
  and explicit remove. Compare full RPM inventory before and after recovery,
  and investigate any residue before retrying.
- Check coexistence with the existing `youtube-dl` RPM: installing and
  removing `yt-dlp` must not remove `youtube-dl` or alter user media. No site
  download is needed for a package-install claim; wider extractor and site
  checks remain H023 in v3.1.
- Add a curated opt-in profile only after VM acceptance; keep `default`
  unchanged. Update the ledger mapping and evidence, generated docs, and
  Windows alignment. Promote to `supported` only after exact-target proof.

The [Fedora package record](https://packages.fedoraproject.org/pkgs/yt-dlp/yt-dlp/)
lists Fedora 44 builds, upstream `yt-dlp`, and the Unlicense. The
[upstream installation guide](https://github.com/yt-dlp/yt-dlp/wiki/Installation)
recognizes package-manager installation. The Fedora RPM route provides the
repository signature check; the operation does not execute a remote script.

## Result

The [acceptance record](../acceptance/package.yt-dlp.md) contains the pinned
image and catalog hashes, overlay, transcript, and one passing focused VM test.
The standalone lifecycle and `youtube-dl` coexistence check passed. The
`video-downloader-yt-dlp` profile selects only the new operation; `default`
and the existing `package.youtube-dl` mapping remain valid. Wider extractor
and site checks stay in H023.
