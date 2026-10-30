# Codec source and broad Multimedia group resolution

Status: **unsupported as a broad v3.0 operation**, 2026-10-30.
The commented v2 `InstallCodecs` uses globs for several GStreamer families,
`lame*`, and a DNF `Multimedia` group upgrade with optional packages.
`RemoveCodecs` removes only some globbed packages and does not invert the
group upgrade or distinguish packages installed by another owner. Some
codec availability may depend on RPM Fusion, whose trust and inverse are
tracked in [provider batch 02](provider-foundation-02.md). Fedora's
accepted [`vlc` package](../acceptance/package.vlc.md) covers its own
Fedora codec set and does not resolve this broad v2 bundle.

## Completion criteria defined before resolution

- Reconcile the exact v2 commands with current Fedora 44 package identities
  and DNF5 group behavior. Preserve the distinction between Fedora and any
  RPM Fusion acquisition source.
- Declare the v2 bundle runnable only if the set of packages is fixed and
  every acquisition source, pre-existing package, transaction effect, and
  inverse can be verified without deleting other owners' codecs. The high-risk
  gate requires focused failure and disposable-VM recovery evidence.
- Otherwise record a non-runnable v3.0 disposition with a specific reason
  and review trigger. Keep independently accepted media applications separate.

## v3.0 decision

Fedora 44 publishes explicit packages for
[`gstreamer1-plugins-base`](https://packages.fedoraproject.org/pkgs/gstreamer1-plugins-base/gstreamer1-plugins-base/),
[`gstreamer1-plugins-good`](https://packages.fedoraproject.org/pkgs/gstreamer1-plugins-good/gstreamer1-plugins-good/),
[`gstreamer1-plugins-bad-free`](https://packages.fedoraproject.org/pkgs/gstreamer1-plugins-bad-free/gstreamer1-plugins-bad-free/),
[`gstreamer1-plugin-openh264`](https://packages.fedoraproject.org/pkgs/gstreamer1-plugins-bad-free/gstreamer1-plugin-openh264/),
and [`lame`](https://packages.fedoraproject.org/pkgs/lame/lame/). The v2
GStreamer and LAME globs do not select only these packages: they can include
other matching builds and a future changed set. DNF5's
[`group upgrade --with-optional`](https://dnf5.readthedocs.io/en/stable/commands/group.8.html)
also selects optional members and upgrades packages already on the machine.
The v2 `RemoveCodecs` omits that group transaction entirely. The source
selection is further entangled with the separate, unaccepted RPM Fusion
repository outcome. There is no complete owned inverse for the broad result.

The `Codecs` source outcome is therefore **unsupported in v3.0**. No v3
operation, profile, VM acceptance, or working install is claimed for this
bundle. The separately accepted `package.vlc` candidate remains its own
application outcome and is not counted as codec-bundle coverage. Review this
decision if a concrete codec requirement is requested, the RPM Fusion trust
contract is accepted where needed, and a fixed package matrix with
data-preserving inverse can be tested on Fedora 44 Workstation. That work
would create individual owned package operations rather than restore the
legacy wildcard and group upgrade.
