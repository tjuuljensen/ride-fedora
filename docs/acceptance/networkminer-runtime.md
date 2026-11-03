# NetworkMiner Fedora runtime package acceptance

The opt-in `forensic-networkminer-runtime` system profile passed on the
disposable Fedora 44 Workstation x86_64 image recorded in
[`package.networkminer.md`](package.networkminer.md). Fedora DNF installed
and removed these signed repository packages:

- `gtk2` 2.24.33-25.fc44
- `mono-core` 6.14.1-4.fc44
- `mono-winforms` 6.14.1-4.fc44

Mono pulled its Fedora runtime dependencies, and GTK pulled its Fedora
integration dependencies. DNF removed those no-longer-needed packages when
the profile was removed. `rpm -q gtk2 mono-core mono-winforms` confirmed the
requested packages were absent afterward. NetworkMiner removal does not
change this system profile; operators manage the runtime profile independently.
