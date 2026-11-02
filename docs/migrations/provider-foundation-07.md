# Provider foundation batch 07: HandBrake deployments

Status: **CLI path operable as an opt-in candidate**, 2026-11-01. The owner kept the v2
`InstallHandBrake`/`RemoveHandBrake` outcome. The v2 pair invokes DNF for
`HandBrake`; its practical intent is the CLI encoder. The current Fedora 44
RPM Fusion free repository keeps the CLI binaries in package `HandBrake` and
publishes a separate `HandBrake-gui` RPM. The
Fedora 44 x86_64 RPM Fusion index lists version 1.11.2 packages. HandBrake's
[official installation guide](https://handbrake.fr/docs/en/1.9.0/get-handbrake/download-and-install.html)
recommends its Flathub edition for desktop users; Flathub publishes app ID
`fr.handbrake.ghb` from the [Flathub manifest](https://github.com/flathub/fr.handbrake.ghb).
RPM Fusion remains an external package source, but the separate
[RPM Fusion source batch](provider-foundation-02.md) now has accepted Fedora 44
trust and owned repository recovery.

## Completion checks defined before implementation

- Preserve the exact v2 CLI capability as an opt-in RPM Fusion package
  operation. Require the accepted RIDE RPM Fusion provider explicitly; never
  add an unverified RPM or implicit repository fallback.
- Offer the official Flathub desktop GUI as a separate system Flatpak
  deployment. Use a distinct deployment ID and keep its app data after
  uninstall. Product review allows the CLI RPM and GUI Flatpak to coexist
  because the CLI package installs no desktop launcher and Flatpak does not
  place its CLI binary on the host PATH.
- Keep the separate RPM Fusion GUI package visible as an alternative, but do
  not combine it with the Flathub GUI until their exported desktop entry and
  update ownership have a conflict review.
- Keep all choices opt-in. Provide a combined profile for users who want both
  the RPM CLI and Flatpak GUI, plus no additions to `default` or `server-base`.
- Focused mocked tests must cover source selection, deployment identity,
  refusal for an untrusted remote/provider, and independent state. A disposable
  Fedora 44 Workstation VM must verify repository setup, both deployments,
  repeat, status, restore, explicit remove, RPM inventory recovery, and
  preservation of pre-existing Flatpak user data. Do not process media or use
  device/hardware acceleration during acceptance.
- Compare Linux and Windows package/deployment contracts and record the
  intentional Fedora CLI/Flatpak GUI split.

## Implementation record

The Fedora 44 RPM Fusion CLI candidate passed its complete disposable-VM
lifecycle, including source/signature verification, command detection, repeat,
status, restore, and explicit remove. Only RPM Fusion's imported public-key
record remains in the RPM database; all HandBrake and dependency RPMs returned
to baseline. See [acceptance evidence](../acceptance/package.handbrake-cli.md)
for the overlay, image, catalog digest, and transcript. The Flathub GUI path
and product-conflict review remain in H067. Fedora 44 RPM Fusion package
source: [HandBrake package index](https://download1.rpmfusion.org/free/fedora/updates/44/x86_64/h/).
