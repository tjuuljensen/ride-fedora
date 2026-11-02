# OpenCTI server operation (post-v3.0)

Status: **planned, non-runnable** on 2026-10-30. OpenCTI is a new generic
server operation, not a v2 function or a member of the scoped v2 migration
ledger. It is **not a v3.0 release blocker** and does not change the v2
outcome denominator. Keep it out of `server-base` and the runnable catalog
until the checks below pass. The catalog ID and deployment identity will be
chosen when the container/runtime boundary is designed; no placeholder
handler is registered.

## Product and deployment boundary

The intended product is OpenCTI Community Edition. Its
[source license](https://github.com/OpenCTI-Platform/opencti/blob/master/LICENSE)
is Apache-2.0 by default; Enterprise Edition has separate terms and is
outside this operation. The [upstream installation guide](https://docs.opencti.io/latest/deployment/installation/)
recommends containers for production and also describes manual packages.
The [deployment overview](https://docs.opencti.io/latest/deployment/overview/)
lists the platform, workers/connectors, search, Redis, RabbitMQ, and object
storage as distinct components. A RIDE operation must select an explicit
deployment method and pin its images or artifacts before claiming support.

The server owner supplies private hostnames, credentials, API tokens,
connector configuration, TLS material, and network exposure. RIDE must not
ship those values in the public catalog or logs. The existing Docker v2
outcome remains a separate, non-runnable v3.0 decision; OpenCTI must not
implicitly install or reconfigure a container runtime.

## Completion checks before runnable status

1. Identify the authoritative deployment source and consumers; select a
   container runtime and exact OpenCTI Community Edition release. Record
   image digests, publisher verification, component licenses, required
   resources, and each dependency's owner.
2. Define separate detection, repeat, upgrade, stop, and inverse behavior
   for RIDE-owned application components. Preserve pre-existing runtime,
   search indexes, queues, object storage, connector state, and backups.
   Removal of application code must not erase threat intelligence data.
3. Keep secrets and site-specific configuration in a private input or
   deployment boundary. Specify service identity, ports, TLS, firewall,
   health checks, and an explicit recovery path for a failed or interrupted
   deployment.
4. Run focused mocked tests and a disposable Fedora Server VM lifecycle
   with seeded data: plan, apply, repeat, health/status, failure, restore,
   and data-preserving removal. Record the exact distro, release,
   architecture, profile, image digests, and outcomes before declaring a
   supported target. Deeper data and security recovery evidence is required
   before the operation is runnable.
5. Compare Linux catalog, profile, and run-state behavior with the Windows
   development branch when implementation begins, and record any shared
   product or schema differences in `docs/windows-alignment.md`.

The next action is a small design batch for the runtime and state boundary,
followed by a separate implementation and VM acceptance batch. The eventual
profile is opt-in and remains independent of `server-base`.
