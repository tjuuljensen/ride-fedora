# Zeek package acceptance

`package.zeek-core` is an opt-in Fedora 44 Workstation x86_64 RPM operation.
Status: supported on Fedora 44 Workstation x86_64 after the lifecycle and
offline trace smoke checks below passed. It remains opt-in through its profile.
It installs Fedora's signed `zeek-core` package and removes only that package
and dependencies DNF considers unneeded. RIDE does not capture live traffic,
read PCAPs, configure file extraction, or manage analyst output. Zeek supports
offline PCAP analysis and file extraction through its File Analysis Framework;
protocol and decoder coverage differs from Xplico.

The declared VM lifecycle checks candidate gating, plan, apply, repeat, status,
RPM signature and package verification, remove, and package
absence. A small synthetic PCAP smoke check confirms the CLI can process an offline
capture and create its connection log. It does not establish extraction
coverage or Xplico protocol parity; H098 tracks a representative fixture and
the remaining protocol gap.

Source: [Fedora 44 `zeek-core`](https://packages.fedoraproject.org/pkgs/zeek/zeek-core/index.html)
documents the core CLI package and its license set. Zeek's official
[File Analysis Framework](https://docs.zeek.org/en/current/frameworks/file-analysis.html)
documents its built-in file extraction analyzer, while the
[offline invocation guide](https://docs.zeek.org/en/master/tutorial/invoking-zeek.html)
documents `zeek -r` for reading a trace file.

Disposable VM run: PASS (Fedora 44 Workstation x86_64, QEMU TCG, pinned image
SHA-256 `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`).
The package transcript was captured while the operation was candidate-gated and verifies first apply, repeat, status,
RPM signature, `rpm -V`, restore, explicit install/remove, and package absence.
The separate synthetic-PCAP run verified that Zeek reads an offline TCP trace
and produces `conn.log`; the trace emitted Zeek's expected warning that it only
contains TCP control packets. It does not validate file extraction.

- Lifecycle transcript: [`transcript.jsonl`](../../.acceptance-runs/resolution-review-01-zeek/lifecycle/transcript.jsonl), SHA-256 `ccbe167a12068e5677a3a171335ca10190fb54aafd177669f615493b9611d49b`
- Synthetic-PCAP transcript: [`transcript.jsonl`](../../.acceptance-runs/resolution-review-01-zeek/synthetic-pcap/transcript.jsonl), SHA-256 `67c87b476b691305e2ba1d735988a3c1db1491234798740316b934aaed87d911`
