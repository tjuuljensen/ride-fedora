---
name: ride-operation-migration
description: Migrate a legacy RIDE function or a Sander-inspired Linux feature into a reviewed v3 catalog operation with tests and migration records.
---

# Migrate one RIDE operation

Use this workflow when converting a v2 function, a server-library function,
or a feature suggested by Sander's library. Read the current catalog and
migration ledger first.

1. State the user-visible outcome and compare the existing functions by
   behavior, not by name. Record the legacy source and intended replacement.
2. Check current authoritative package or upstream documentation. Choose a
   trusted provider and supported distro/release/architecture. Record product,
   source, license, and the verification evidence available at acquisition.
   Preserve attribution for adapted code; do not copy unlicensed source.
3. Add a stable catalog ID and a fixed handler mapping. Implement current-state
   detection, desired-state application, failure reporting, and a supported
   inverse. Mark operations without a reliable inverse accordingly.
4. Add a mocked lifecycle test and, when system behavior matters, disposable
   VM acceptance evidence. Keep untested targets and no-op candidates out of
   executable profiles.
5. Update generated operation docs, the legacy mapping, and the migration
   ledger. Report unresolved behavior or external-source evidence plainly.
