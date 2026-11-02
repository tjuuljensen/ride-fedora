# `package.tripwire` acceptance

Status: **CANDIDATE LIFECYCLE PASSED** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 publishes Open Source Tripwire 2.4.3.7-21.fc44 under repository
signatures, licensed GPL-2.0-or-later. Upstream source and releases are
[Tripwire Open Source](https://github.com/Tripwire/tripwire-open-source/).

The candidate operation manages RPM presence only. It must not create keys or
an integrity database, initialize policy, execute the packaged daily check,
or scan files. The first pilot stopped at `rpm -V`: the Fedora RPM's post-
install scriptlet intentionally replaces `localhost` in
`/etc/tripwire/twpol.txt` with the system hostname. The RPM database confirms
this exact scriptlet:

```sh
/usr/bin/sed -i -e "s|localhost|$HOSTNAME|g" /etc/tripwire/twpol.txt
```

The installed package had no generated key files or `.twd` baseline. Acceptance
permits only the expected RPM verification record for the scriptlet and
asserts the hostname value. The full apply/repeat/restore/install/remove
lifecycle passed with exact RPM inventory recovery. Fedora's RPM preserves
the hostname-specific sample policy as an unowned
`/etc/tripwire/twpol.txt.rpmsave` on removal; the lifecycle check asserts that
the residue contains the expected hostname and no private keys or baseline.
This behavior is documented for the opt-in candidate. H066 tracks baseline,
key, policy, and scheduled-check recovery for v3.1.

Transcript: `../.tmp-vm-acceptance-security-06ao-verified/fedora-44-workstation-x86_64/20261101T125939Z-test-package-apply-repeat-status-restore-and-remove-69bfa7b3/transcript.jsonl`
(SHA-256 `432eb5613b45126f39716642445080c0302140c9884c39dd0fd47064cbd7eccb`).
