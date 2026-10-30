# Snapd service and package-manager ownership

Status: **high-risk isolated assessment pending**, 2026-10-30.
The commented v2 `InstallSnap`/`RemoveSnap` pair installs or removes the
Fedora [`snapd` RPM](https://packages.fedoraproject.org/pkgs/snapd/snapd/).
Snapd is a privileged package manager with service and application state;
package presence alone does not prove a usable or safely removable Snap
installation. The v3.0 catalog has no runnable operation for this outcome.

Before implementation, define service activation and confinement behavior,
detect pre-existing snapd and user-installed snaps, preserve all unowned
snap data and service configuration, and specify an inverse that never
removes other owners' apps. Use focused mocked failure tests and an isolated
disposable Fedora 44 x86_64 Workstation VM with seeded app/data state and
recovery. If this high-risk evidence cannot be completed for v3.0, record a
reasoned non-runnable disposition with a review trigger; do not use an
opt-in candidate to bypass the safety gate.
