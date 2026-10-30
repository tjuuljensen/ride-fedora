# Flatpak runtime and application-preserving inverse

Status: **high-risk recovery assessment pending**, 2026-10-30.
The commented v2 `InstallFlatpak` installs the Fedora Flatpak RPM. Its
`RemoveFlatpak` runs `flatpak uninstall --all` before `dnf autoremove -y
flatpak`, so it can delete applications and runtimes RIDE did not install.
The current [Fedora Flatpak package](https://packages.fedoraproject.org/pkgs/flatpak/flatpak/)
is available for Fedora 44 and is pre-installed in the pinned Workstation
image. Pre-installation in one image does not prove a safe v3 installation
or inverse on all declared hosts.

Before a runnable v3 operation, choose an installed-only runtime contract or
an ownership-aware package inverse. In a disposable Fedora 44 x86_64
Workstation VM, seed a user-owned Flatpak application and remote, apply the
selected runtime behavior, and prove the app, remote, and user data survive
repeat, failure, and recovery. Never use `uninstall --all` or a blanket
autoremove as RIDE's inverse. If preservation cannot be proved for v3.0,
record a reasoned non-runnable disposition and a review trigger.
