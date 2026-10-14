# GitHub release discovery contract

RIDE Linux and RIDE Windows use the same product-level rules while keeping
their implementations native to Bash and PowerShell. The comparison source
is `ride-windows/docs/github-release-discovery.md` on its development branch;
this document records the Linux candidate.

| Behavior | Shared rule | Linux implementation |
| --- | --- | --- |
| Endpoint | Exact declared public GitHub `releases/latest` endpoint over HTTPS | Fixed repository field in catalog and `api.github.com` URL construction. |
| Freshness | Five minutes, no expired fallback | Private disk cache across CLI invocations; timestamp checked against current clock. |
| Bounds | Up to 64 endpoints, 2 MiB per response | Oldest cached files evicted; oversized or malformed responses rejected. |
| Rate limits | Fresh cache remains usable; uncached requests fail during backoff | One disk deadline across endpoints for each authentication context. |
| Authentication | Anonymous default, explicit PAT context | `RIDE_GITHUB_TOKEN` may be set for one invocation; no automatic token discovery or token persistence. Cache keys separate token values. |
| Provenance | Endpoint, acquisition kind, fetch and expiry times, quota observations, authentication mode | JSON metadata and artifact `.ride.json` sidecar; no credential value. |
| Verification | Hash evidence never implies independent publisher signature | Download requires GitHub API `sha256:` digest and local SHA-256 match. |

Linux disk cache is intentionally different from Windows' process cache.
Authentication storage is also different: the Linux client has no credential
enrollment facility yet, so users must explicitly provide a short-lived token
for a single process. Never put a token in a catalog, profile, command
argument or committed file. Release metadata and artifact cache are separate.
PAT backoff is separated by token context rather than GitHub account identity;
rotating tokens does not create a new GitHub account quota. The Linux client
does not claim account-wide backoff tracking yet.
No shared runtime module is planned until both clients' contracts stabilize.

Product identifiers, official homepage, source, license and verification
claims should be reviewed across repositories. Package selectors, supported
platforms, service handling and install methods remain platform-owned.
