# Chrome recommended policy acceptance

Target: Fedora 44 Workstation x86_64. Scope: one RIDE-owned host policy file
and Chrome Flatpak policy ingestion; no profile sign-in or personal browsing.

Status: PASS, Fedora 44 Workstation x86_64 disposable VM.

Operation: `setting.chrome-preferences`.

- Plan and candidate gate behaved as declared.
- Apply created the exact recommended policy file and a mode 0600 ownership
  manifest.
- Status reported the setting configured; repeat reported no change.
- `flatpak info --show-permissions com.google.Chrome` confirmed `host-etc`.
- Direct `unset` deleted the policy and ownership manifest; repeated unset was
  unchanged. Restoring the unset run recreated the selected policy list, and
  restoring the original apply run returned it to absent.
- Transcript: `.acceptance-runs/align03-owned-unset/fedora-44-workstation-x86_64/20261105T144349Z-test-chrome-preferences-policy-lifecycle-and-flatpak-import-27a0e62e/transcript.jsonl`
- Transcript SHA-256: `336d02a93bdc877b2b692cfc68168749f249acf5e2a0f2a1d631c67a9d9aa18a`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

The visible `chrome://policy` review and current Safe Browsing policy mapping are
tracked as H091 for v3.1 hardening.
