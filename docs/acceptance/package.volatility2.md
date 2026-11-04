# `package.volatility2` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 x86_64 Workstation,
2026-11-01. The candidate is limited to the core Volatility 2.6.1 CLI on an
isolated PyPy 2.7 runtime. It makes no claim about optional plugins, profiles,
or memory-image analysis.

The disposable TCG VM verified candidate refusal, absent plan, user-scope
install, both pinned archive digests, the 2.6.1 `--info` banner, installed
status, unchanged repeat, explicit removal, and preservation of an unrelated
user file. `--info` listed the framework's optional plugin import warnings
because legacy packages such as `Crypto` and `distorm3` were not installed;
the core command still returned success. No memory image was read or changed.

Image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Catalog SHA-256: `131dca38abeefbfba261544f4b41025534ace62aef404dfce9e79d370446ff62`.
Source bundle SHA-256: `8a7db979affd0cad46018b6e72f6f7ff7c2f95f44b953ea789e62c3e9093084e`.
Transcript SHA-256: `92086aecee80b14ef5a03168dd3a277a4ec8ebd277913d954223c1a6c95e6683`.
The retained transcript and overlay are under
`.acceptance-runs/legacy-vm/.tmp-vm-acceptance-forensic-02-volatility2/fedora-44-workstation-x86_64/20261101T211914Z-test-volatility2-pypy-bundle-lifecycle-8e070722/`.

The focused mocked test confirms removal refuses a pre-existing unowned
destination. Broader plugin compatibility, changed-bundle integrity checks,
and representative disposable memory-fixture analysis remain in H088.
See the [batch record](../migrations/forensic-isolated-02.md).
