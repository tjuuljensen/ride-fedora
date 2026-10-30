# Package deployment and acquisition decisions

This is the Linux counterpart of the approved decisions in
`ride-windows/docs/MIGRATION-PLAN.md` ("Package variants and portable lifecycle"
and "Multiple package sources") and
`ride-windows/docs/migrations/package-deployment-decisions.md`, reviewed on
2026-10-14. It defines the shared product behavior; Bash providers and Linux
target evidence remain local to this repository.

Compare the Linux and Windows data models at every package migration batch and
before release candidates. Track deliberate differences and their review
triggers in [Windows alignment](windows-alignment.md); unexplained behavioral
drift blocks promotion of a package operation.

## Independent dimensions

| Dimension | Meaning | Current Linux example |
| --- | --- | --- |
| Product ID | Stable logical product outcome | `package.imhex` |
| Distribution | Installed application or portable files | `installed` |
| Deployment | One owned instance of that distribution | `local-installed` |
| Provider | Approved route to an exact artifact/build | `fedora-rpm` |
| Artifact format | Bytes acquired or installed | `rpm`, `wheel` |
| Scope | System or intended user | `system` for DNF, `user` for Volatility3 |
| Destination | Package-manager identity or owned path | RPM name or Volatility3 environment |

One product may have an installed deployment, separate portable deployments,
and multiple acquisition kits. They may coexist when a product-specific review
shows that paths, registrations, services, drivers, and shared configuration do
not conflict. Each deployment needs separate ownership, distribution, scope,
destination, version, artifact evidence, and recovery. Removing or updating one
must not mutate another or delete user-created data. Product-only requests that
cannot identify one deployment must fail instead of choosing one silently.
Replacing one deployment with another is an explicit migration.

The current Linux engine has only one `installed` deployment slot per package.
Its alternate provider check is scoped to that slot. It is a temporary guard
against ambiguous provider/build state, not a rule that portable and installed
editions are mutually exclusive. Portable deployments and kit assembly require
their own identifiers, destination selection, manifests, handlers, state
migration, and VM evidence before the runtime can allow coexistence.

## Acquisition and installation

`download` acquires bytes; it never establishes installed package state. A
download manifest must bind product, distribution, provider, version,
architecture, exact source URI, filename, observed digest, and any independent
publisher or repository verification evidence. A RIDE-computed SHA-256 is an
observation, not publisher authentication.

Normal installation may resolve and acquire an approved artifact. A separate
offline install mode must consume an already retained, verified exact artifact
and must not contact the network or silently fetch dependencies. The current
Fedora RPM download produces a signature-checked file and SHA-256 sidecar;
`install` still invokes DNF by package name, so offline install is pending.
The GitHub `artifact` operation is download-only and cannot appear in a profile.

Explicit provider choices never fall back. A future automatic choice may try
another approved provider only after acquisition availability or transport
failure, and only for an equivalent package/version, distribution, scope, and
verified artifact. Installation failure, version mismatch, hash mismatch,
invalid signature, and unexpected publisher stop the operation. Different
builds need distinct artifact metadata even under one product ID. The resolved
provider and exact artifact digest belong in the download and run records.
There is no automatic fallback or local provider preference in Linux v3 yet.

## Current schema and compatibility

Catalog schema 3 records the current `installed` distribution,
`local-installed` deployment ID, artifact format, and default `sourceId`.
`sourceProviders` can describe reviewed alternatives for that same deployment
and scope. Profiles without `source` keep the catalog default; an explicit
undeclared source fails. Run schema 2 records distribution, deployment, scope,
source, and a signature of the selected definition. Restore can read schema 1
runs and compare their earlier signature format. Neither schema claims portable
coexistence or offline install support.

Before adding a portable or second installed deployment, define explicit
selection in commands and profiles, per-deployment observation and manifests,
and a migration for saved selections and recovery records. Plans must report
distribution, provider, scope, destination, and deployment identity. Removal
and restore must use the recorded selection rather than current preferences.
Add read-only completion for enumerable choices. A local data-only,
schema-versioned configuration may later hold user or system preferences;
there is no implicit provider or deployment switch in the current client.

## Acceptance

Review coexistence per product. Mock source selection, strict explicit
choices, provider fallback/refusal, separate deployment lifecycle, modified
files, partial failure, and offline installation. Exercise each offered
provider/distribution on its declared distro, release, edition, and CPU
architecture in disposable VMs before marking it supported. Portable
acquisition suitability and redistribution rights need separate evidence from
file deployment alone.
