# Fedora 44 acceptance: package.fpdns

**Result: PASS**

Disposable VM run: PASS on Fedora 44 Workstation x86_64.

`package.fpdns` passed RPM signature verification, `rpm -V`, local usage or
version probing, status, repeat apply, and restore in the combined
[Security Lab DNS utilities acceptance](security-lab-dns-tools.md). The
combined report records the three Fedora Perl dependency upgrades caused by
DNSenum and confirms no other package changes remained after restore.
