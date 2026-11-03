# Email header analyzer local SPA

Status: **operable opt-in candidate on Fedora 44 Workstation x86_64**, 2026-11-02.
The owner kept this capability in the v3.0 fast-track review on 2026-10-30.
The pinned MailTower frontend now supplies a local replacement for the v2
persistent Flask service.

## Completion checks

- Pin a licensed source and verify the complete source tree and its build path.
- Confirm raw headers are not transmitted, retained, logged, or placed in URLs.
- Preserve the v2 use case: human-readable header analysis, server route, hop
  delays, and origin information.
- Install to an owned local destination and remove only that destination.
- Test malformed and large synthetic headers, mocked acquisition failure, and
  exact removal; run a brief offline launch check on disposable Fedora 44
  Workstation x86_64.
- If the selected path requires a persistent service, keep its loopback bind,
  service identity, unit ownership, failure handling, data behavior, and
  recovery inside the high-risk acceptance boundary.

## Current source assessment

The [CyberDefenders upstream project](https://github.com/cyberdefenders/email-header-analyzer)
still documents a Flask development server and an optional `0.0.0.0` bind.
Its README retains the older `lnxg33k` clone URL and pip-based setup. GitHub's
master history shows its latest commit in 2020, and no current tagged release
was found. GitHub does not clearly identify the repository license, so do not
package or adapt that source before reviewing its license text.

A possible replacement is the [MailTower Email Header Analyzer](https://github.com/mailtower-app/email-header-analyzer).
The source reviewed here is pinned to commit
[`ccaf044dfe964215656966013feaaea705726048`](https://github.com/mailtower-app/email-header-analyzer/commit/ccaf044dfe964215656966013feaaea705726048)
(tree `69ec6b8a3c078a0f952e04ddea47f0a0ebf3ce49`, latest `main` at review
time, unsigned, with no tagged release). The repository's [LICENSE](https://github.com/mailtower-app/email-header-analyzer/blob/ccaf044dfe964215656966013feaaea705726048/LICENSE)
is MIT. The tracked app is a Vue/Quasar single-page frontend; the Docker setup
serves the built SPA with nginx and contains no analysis backend. The analyzer
parses the pasted header in browser code and preserves the v2 route/hop-delay
use case.

The tracked frontend source was searched for `fetch`, XHR, Axios, WebSocket,
`sendBeacon`, browser storage APIs, and service-worker use; none were found.
The only external URLs in app components are links to MailTower and GitHub.
This source review supports a local-only design, but does not prove built
runtime behavior or transitive dependency safety. `package-lock.json` pins
313 npm packages; each resolved package has an integrity digest and none use
Git dependencies. Its install-script metadata identifies the root Quasar
preparation step plus two dependency scripts (`@parcel/watcher` and optional
`fsevents`). A safer build attempt can use `npm ci --ignore-scripts` and invoke
the root Quasar preparation step explicitly, but this has not been built or
verified yet. Transitive licenses and dependency behavior still need review.
Building requires Node and `npm ci`; those registry requests happen during
acquisition/build, not when analyzing a header. The repository uses
history-mode routing, so a local static server with SPA fallback is required;
the upstream Docker/nginx config already demonstrates that serving model.

The v2 setup changes global pip state, clones an unpinned repository into
`/opt`, writes a systemd unit, and may expose a web service. Its inverse does
not remove the venv, global Python changes, or a safely inventoried user-data
path. The reviewed MailTower frontend supports a local owned application; the
old service deployment is not being carried forward as-is.

## Implemented and verified for v3.0

The reviewed source now has the candidate operation
`package.email-header-analyzer` and opt-in profile
`fedora-email-header-analyzer`. The operation clones and verifies the pinned
commit, tree, and npm lockfile blob, builds with npm lifecycle scripts
suppressed except for explicit Quasar preparation, and installs only the SPA,
launcher, and an ownership manifest. The Python launcher serves on an
ephemeral `127.0.0.1` port, sends a restrictive CSP, does not log request
paths, and holds a shared file lock so removal refuses while it runs.

Three focused mocked tests pass for pinned acquisition/build failure cleanup,
repeat and ownership checks, mocked loopback binding and SPA fallback, CSP
headers, running-server removal refusal, and preservation of unrelated files.
The separate disposable-VM acceptance builds the real source and exercises its
HTTP listener. The operation is an opt-in **candidate**; H114 tracks real
browser parser fixtures and dependency-license review.

The disposable Fedora 44 Workstation x86_64 acceptance passed under QEMU TCG:
**1 passed in 451.97 seconds**. It built the pinned source on the target,
exercised candidate gating, apply/repeat/status, a real loopback HTTP listener,
CSP and history-route responses, clean stop, exact owned removal, and seeded
Firefox-profile preservation. The passing transcript and VM overlay are
recorded in [acceptance evidence](../acceptance/package.email-header-analyzer.md).

The acceptance did not automate actual browser input or verify parser output;
that and transitive dependency-license review are named H114 v3.1 hardening.
The real listener is now covered, so the earlier sandbox-specific mocked-server
limitation is no longer a v3.0 blocker.
