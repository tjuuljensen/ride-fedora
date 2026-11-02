# Fedora 44 acceptance: package.httpie

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64.

`package.httpie` passed signature verification, `rpm -V`, local help probing,
status, repeat apply, and restoration in the combined
[Security Lab network clients acceptance](security-lab-network-clients.md).
The package was absent before apply and removed during restore. HTTPie's
shared `python3-requests` dependency update is recorded in the combined report.
