# `package.wireshark-cli` Fedora 44 acceptance

Status: **PASS; opt-in candidate** on Fedora 44 Workstation, x86_64,
2026-10-31.

Target: Fedora 44 Workstation, x86_64. Package: `wireshark-cli` from Fedora's
signed Fedora 44 repository. Fedora packages it as the command-line component
of Wireshark, including `tshark`; product documentation is at
<https://www.wireshark.org/> and the Fedora package record is at
<https://packages.fedoraproject.org/pkgs/wireshark/wireshark-cli/>.

The operation passed candidate gating, signed Fedora RPM installation,
root-run RPM file verification, the `tshark --version` probe, idempotent
repeat, status, and exact inverse as part of the focused Security Lab profile
run. It is opt-in and does not enable capture permissions or start capture
traffic. See [Security Lab network profile acceptance](security-lab-network.md)
for the run ID and transcript path.
