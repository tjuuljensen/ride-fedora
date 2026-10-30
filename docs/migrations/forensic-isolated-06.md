# Email header analyzer service and Python environment

Status: **unsupported for v3.0**, 2026-10-30. The commented v2
`InstallEmailHeaderAnlzr` changes global pip state, clones an unpinned
repository into `/opt`, writes a systemd unit, and may expose a web
service. This is a service and data ownership change, not just a Python
package. Review the current upstream license and release, exact bind
address, service identity, network exposure, user data, and inverse before
declaring a runnable operation.

The safety gate requires a pinned isolated environment, owned unit and
destination, no unrequested public network bind, focused failure tests, and
a disposable Fedora 44 x86_64 Workstation VM with service and recovery
evidence. If that cannot be established for v3.0, record a reasoned
non-runnable disposition and review trigger; do not use a candidate to
bypass the service security gate.

## Decision

The [current upstream project](https://github.com/cyberdefenders/email-header-analyzer)
describes a Flask development server and optional `0.0.0.0` bind. The v2
function clones the old `lnxg33k` URL without a pin, upgrades global pip,
installs dependencies outside its intended venv, and writes a persistent
systemd unit and desktop launcher. Its inverse does not remove the venv,
global Python changes, or a safely inventoried user-data path. No chosen
service identity, loopback-only bind, pinned dependencies, unit ownership,
or exact-target recovery test exists. This high-risk outcome is
**non-runnable unsupported in v3.0**. Reopen for a requested local service
with a licensed pinned source, isolated dependencies, loopback bind,
seeded-data preservation, and disposable-VM start, failure, and removal
evidence.
