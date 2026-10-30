# Email header analyzer service and Python environment

Status: **isolated review pending**, 2026-10-30. The commented v2
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
