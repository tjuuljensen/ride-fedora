# Generic Server 12: Selenium Python bindings

Status: **opt-in candidate passed**, Fedora 44 Server x86_64. This batch preserves the kept v2 `InstallSelenium` binding install
through Fedora's signed `python3-selenium` RPM. The old global unpinned pip
install is replaced with the distribution package.

## Completion checks and result

- Confirm the RPM is present in Fedora 44 Server and signed by Fedora.
- Require opt-in candidate consent, then verify apply, repeat, status, Python
  import, restore, and explicit remove on the exact Server VM target.
- Preserve every RPM that predated the operation.
- Keep browsers, drivers, Selenium Grid, application code, and WebDriver session
  downloads outside this package operation and its profile.

All checks passed on the pinned Server target. The guest initially lacked the
RPM; candidate consent was required for apply, restore, direct install, and
remove. The binding imported as version 4.20.0, RPM verification passed, and
the original package set was preserved.

The current Fedora 44 package is `python3-selenium` 4.20.0-11.fc44, licensed
Apache-2.0. The [Fedora package record](https://packages.fedoraproject.org/pkgs/python-selenium/python3-selenium/)
is the acquisition and license reference. Upstream advises using a virtual
environment for pip deployments and notes that current bindings can obtain
browser/driver artifacts with Selenium Manager; Fedora's DNF-managed package is
used here instead of creating a global pip environment. See the [Selenium
Python install documentation](https://www.selenium.dev/selenium/docs/api/py/).

The full [disposable VM transcript](../../.acceptance-runs/fedora-44-server-x86_64/20261102T103916Z-test-server-selenium-bindings-lifecycle-68b8d262/transcript.jsonl)
records the lifecycle. This opt-in package does not claim a working browser automation stack. If the
owner later requests RIDE-managed browser or driver pairing, add that as a
separate operation with its own source, target, network, and cleanup contract.
