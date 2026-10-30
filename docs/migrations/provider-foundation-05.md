# Codec source and broad Multimedia group resolution

Status: **high-risk assessment pending**, 2026-10-30.
The commented v2 `InstallCodecs` uses globs for several GStreamer families,
`lame*`, and a DNF `Multimedia` group upgrade with optional packages.
`RemoveCodecs` removes only some globbed packages and does not invert the
group upgrade or distinguish packages installed by another owner. Some
codec availability may depend on RPM Fusion, whose trust and inverse are
tracked in [provider batch 02](provider-foundation-02.md). Fedora's
accepted [`vlc` package](../acceptance/package.vlc.md) covers its own
Fedora codec set and does not resolve this broad v2 bundle.

Before any runnable v3 operation, enumerate exact Fedora 44 and any approved
third-party codec products, source licenses, package identities, and
verification requirements. Split the glob/group behavior into owned
operations; exclude unowned packages and transaction-wide upgrades from
remove/restore. Use focused failure tests and disposable Workstation VM
evidence for every declared source and inverse. If a safe source or inverse
cannot be established for v3.0, record a reasoned non-runnable disposition
with a review trigger. Do not use a candidate to bypass this high-risk gate.
