# `package.yubico-authenticator` acceptance

Status: **PASS; operable opt-in candidate on Fedora 44 Workstation x86_64**, 2026-11-01.

The operation installs Yubico Authenticator 7.4.1 under the user's private
`~/.local/opt/ride-fedora/yubico-authenticator/7.4.1` path and owns only that
tree, a user-local launcher, desktop entry, icon, and RIDE ownership records.
It verifies the pinned SHA-256 and Yubico detached OpenPGP signature against
primary fingerprint `20EE325B86A81BCBD3E56798F04367096FBA95E8`. It does not run
the upstream desktop integration script, enable `pcscd`, launch the GUI, or
configure a connected YubiKey. Existing app preferences and unrelated
`~/Applications` files remain outside the owned paths.

The disposable Fedora 44 Workstation acceptance passed the candidate gate,
install, exact owned tree and launcher paths, repeat, status, removal, and
synthetic user-state preservation. It uses no physical key and performs no
credential operation. The GUI was not launched; this package operation makes
no claim about hardware access or user-visible key behavior.

Exact target: Fedora 44 Workstation x86_64, image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
Transcript: `.tmp-vm-acceptance-publisher-08-yubico-gui-final/fedora-44-workstation-x86_64/20261101T174434Z-test-yubico-authenticator-owned-archive-lifecycle-146c4cc8/transcript.jsonl`, SHA-256
`0adc637de1789b294242dfcfabde888666eb97f3b5a5abfde042d50610c1343e`.
Candidate catalog SHA-256: `eb84fbfc8c7dfe6170318d565968771d6fad7e93f1a1df42e701879fc3853fab`.
