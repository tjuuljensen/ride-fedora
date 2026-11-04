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
- Remove deleted the policy and ownership manifest; status reported absent.
- Transcript: `.acceptance-runs/legacy-vm/.tmp-vm-acceptance-desktop-user-05-chrome/fedora-44-workstation-x86_64/20261101T230926Z-test-chrome-preferences-policy-lifecycle-and-flatpak-import-4a1f7886/transcript.jsonl`
- Transcript SHA-256: `193970bac9d2751a186f09998d5b33d8f23a4c5e77b0bfdeadf6e6a15c3bc3a1`
- Base image SHA-256: `78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`

The visible `chrome://policy` review and current Safe Browsing policy mapping are
tracked as H091 for v3.1 hardening.
