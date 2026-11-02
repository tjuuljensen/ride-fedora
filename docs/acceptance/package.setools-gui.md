# SETools GUI package acceptance

`package.setools-gui` is a Fedora 44 Workstation x86_64 candidate RPM operation
from Security Lab batch 06AG. Fedora ships version 4.6.0-6.fc44 under
GPL-2.0-only, rebuilt against current SELinux userspace. The active upstream
provides the `apol` graphical SELinux policy analysis tool. RIDE manages RPM
presence only and does not launch Apol or inspect policy data.

Package lifecycle, signature, `rpm -V`, status, repeat apply, restore, and
presence of `/usr/bin/apol` passed in the shared [06AG acceptance
report](security-lab-security-desktop-tools.md). The RPM had no file
capabilities, scriptlets, or systemd units. DNF updated 11 pre-existing Qt and
GStreamer RPMs to satisfy its transaction; restore removes newly installed
packages but does not reverse those updates. H059 tracks this recovery effect
and later read-only policy-fixture behavior, so the operation stays
candidate-gated.
