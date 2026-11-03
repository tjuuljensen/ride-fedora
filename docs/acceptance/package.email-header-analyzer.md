# Email header analyzer

- Target: Fedora 44 Workstation x86_64.
- Scope: opt-in user-local static web app; no system package or service.
- Upstream: MailTower `ccaf044dfe964215656966013feaaea705726048`, tree
  `69ec6b8a3c078a0f952e04ddea47f0a0ebf3ce49`; MIT frontend license.
- Dependency lock: 313 npm packages with registry integrity digests and no Git
  dependencies. Their licenses and install-script behavior still need review.
- Build prerequisites: `git`, Node.js 22.12+, 24.x, or 26+, npm, and Python 3.
- Runtime: Python standard library serves the built SPA on an ephemeral
  `127.0.0.1` port. The launcher opens the local URL in the default browser.
  Content Security Policy denies non-local connections; request paths are not
  logged. Stop the foreground server with Ctrl+C before removal.
- Owned paths: `~/.local/share/ride-fedora/apps/email-header-analyzer`,
  `~/.local/bin/ride-email-header-analyzer`, and
  `~/.local/share/ride-fedora/owned-tools/package.email-header-analyzer.json`.
- Recovery: removal refuses a modified install or an active local server and
  removes only the exact RIDE-owned app tree, launcher, and manifest.

## Fedora build prerequisites

On Fedora 44 Workstation x86_64, the checked build path uses the signed Fedora
RPMs `git`, `nodejs24`, `nodejs24-bin`, `nodejs24-npm`, and
`nodejs24-npm-bin`. Install them before applying the app profile. Node.js 24
satisfies the pinned frontend's supported build range; the app operation does
not install or remove system build tools.

## Verified evidence

Three focused mocked lifecycle tests pass. The Fedora 44 Workstation x86_64
RIDE acceptance passed: **1 passed in 451.97 seconds**, under QEMU TCG and the
pinned image SHA-256
`78356d69277dd0c5f103a6fdf0c603424a1aad8e02242ae893b8335ffca7c178`.
The test installed the Node.js prerequisites, verified the candidate gate and
pinned commit/tree, built the locked source with dependency lifecycle scripts
suppressed, applied and repeated the profile, checked status, served the SPA
on IPv4 loopback, fetched its history-mode route, checked its CSP response,
stopped the server, and removed only the owned app, launcher, and manifest. A
seeded Firefox-profile marker remained unchanged. It did not automate actual
browser input or parser output; that remains in H114.

Acceptance run ID: `20261102T183317Z-2550-6905`. Evidence is retained under
`.acceptance-runs/email-header-analyzer/fedora-44-workstation-x86_64/20261102T183317Z-test-email-header-analyzer-local-spa-lifecycle-85f365f2/`.
Transcript SHA-256: `036bbd6bb728a52b363f4db3e48fb62a14de1a1d0b74853dde1ecb20439241f7`;
metadata SHA-256: `36b52da22ffdf7df2acf4b8e9193c8fa8ea9848ca3c4f574bf940e6ba4966b56`;
overlay SHA-256: `5a4ee0e439807e8a1b92872cbdde057bc9d51f93737ba6573b2b72742a881643`.

Safety review checks: `private-output-boundary` (the app and manifest stay in
user-owned mode-0700 and mode-0600 RIDE paths, and the listener binds only to
127.0.0.1); `no-evidence-processing` (the RIDE operation and launcher do not
read or scan local message or evidence files; the SPA analyzes only text the
user chooses to paste); and `exact-output-preservation` (removal deletes only
the verified owned app/launcher/manifest and leaves the seeded Firefox profile
marker unchanged). The SPA source review found no outbound network or browser
persistence APIs; H114 covers real-browser parser fixtures and transitive
license review.

Keep the operation as an opt-in candidate. The installed source is the MIT
MailTower frontend; the v3.0 operation rebuilds it locally and does not ship a
prebuilt publisher artifact. `npm ci --ignore-scripts` plus explicit Quasar
preparation suppresses dependency install scripts. Broader dependency-license
review, parser fixture accuracy, and visual behavior remain in H114.
