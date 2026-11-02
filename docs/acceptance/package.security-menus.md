# Fedora Security Lab menu package acceptance

`package.security-menus` is a Fedora 44 Workstation x86_64 candidate RPM
operation from Security Lab batch 06AG. Fedora ships version 38-8.fc44 under
GPL-2.0-only. The Fedora package adds the Security Lab XDG menu category and
includes launcher entries for the wider Security Lab package collection.
Fedora's package page points to a read-only Pagure archive, but Fedora
continues to build and ship the RPM. RIDE manages package presence only; it
does not launch menu entries.

Package lifecycle, signature, `rpm -V`, status, repeat apply, and restore
passed in the shared [06AG acceptance report](security-lab-security-desktop-tools.md).
The RPM had no file capabilities, scriptlets, or systemd units. Its dependency
transaction updated 11 existing Qt/GStreamer RPMs; restore does not roll back
those updates. The desktop menu's visible layout and behavior remain queued
under H059, so the operation stays candidate-gated.
