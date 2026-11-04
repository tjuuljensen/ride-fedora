# `package.yubikey-manager` acceptance

Status: **PASS; supported on Fedora 44 Workstation x86_64**, 2026-11-01.

This operation installs Fedora's signed YubiKey Manager CLI (`ykman`) RPM.
It manages package presence only. It does not inspect, configure, personalize,
reset, or otherwise communicate with a connected YubiKey. The explicit
`fedora-yubikey-tools` profile stays opt-in and outside base profiles.

The disposable Fedora 44 Workstation acceptance started from an absent RPM,
then checked candidate-gated apply, RPM signature and files, `ykman --version`,
repeat, status, and exact remove-new-install recovery. Candidate gating has
since been removed after this passing lifecycle; the DNF handler is unchanged.
The shared transcript retains the candidate-run evidence. A physical key is not needed for this
package-only scope; any future RIDE-managed key configuration needs a separate
operation and explicit hardware evidence.

Exact target: Fedora 44 Workstation x86_64, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.

VM result: **PASS**. The shared `test_yubikey_manager_cli_package_lifecycle`
transcript is `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-publisher-08-yubikey-cli/fedora-44-workstation-x86_64/20261101T172904Z-test-yubikey-manager-cli-package-lifecycle-16bb7196/transcript.jsonl`, SHA-256
`e737a4236375c72ef87a091a77ea756c3748b072bb764feea9d97a5942c95d54`.
