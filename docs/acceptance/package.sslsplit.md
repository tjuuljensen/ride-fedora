# sslsplit package acceptance

`package.sslsplit` is a Fedora 44 Workstation x86_64 candidate operation from
Security Lab batch 06AB. Fedora repository signatures were present, root-run
`rpm -V` passed, and the RPM declared no file capabilities or scriptlets.
Install, repeat, and removal recovery passed in the disposable VM. RIDE manages
the RPM only; it does not run network behavior. See the shared
[06AB package acceptance report](security-lab-network-interception.md) and
retained transcript listed there. H053 tracks authorized operation and
network recovery before tool behavior is offered.
