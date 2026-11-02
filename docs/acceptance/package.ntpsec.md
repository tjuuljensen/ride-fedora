# `package.ntpsec` acceptance

Status: **PASS; operable opt-in candidate** on Fedora 44 Workstation x86_64,
2026-11-01.

Fedora 44 publishes NTPsec 1.2.6-1.fc44 under Fedora repository signatures.
The Fedora license expression is NTP AND BSD-2-Clause AND BSD-3-Clause AND
BSD-4-Clause AND ISC AND Apache-2.0 AND Beerware. The upstream project is
[NTPsec](https://ntpsec.org/), with source and release links on its
[downloads page](https://ntpsec.org/downloads.html).

The v3 operation manages RPM presence only. Its opt-in profile did not start
or enable `ntpd`, alter existing chronyd state, configure time sources, contact
peers, or synchronize the system clock. The lifecycle passed; Fedora created a
persistent `ntp` nologin account that remained after package removal. H063
tracks expanded service, account, configuration, and clock recovery for v3.1.
See the [06AK batch report](security-lab-ntpsec.md).
