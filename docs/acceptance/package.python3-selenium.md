# Selenium Python bindings on Fedora 44 Server

Status: **opt-in candidate passed**, Fedora 44 x86_64 Server for
`package.python3-selenium`. The operation installs Fedora's signed
`python3-selenium` RPM. It does not install a browser, driver,
Selenium Grid, or application-specific test code. Browser and driver selection
remains the consuming workload's responsibility; Selenium Manager may download
browser artifacts when application code requests a WebDriver session.

## Completion checks

- The exact Server target plans the opt-in package and requires candidate consent.
- Apply and repeat install only `python3-selenium`; import the installed module
  and verify the Fedora RPM signature and package files.
- Status reports installed. Restore and explicit remove delete the package only
  when RIDE introduced it and preserve pre-existing RPMs.
- No browser, driver, Grid service, or user's test environment is changed.

## Fedora 44 Server result

The disposable Server lifecycle passed on 2026-11-02. It confirmed the
candidate-consent refusal, installed signed `python3-selenium` 4.20.0-11.fc44,
verified the RPM file list and Python import, exercised repeat and status,
restored the initial absence, then explicitly installed and removed the
operation. The baseline RPM set was preserved. The full command transcript is
[`transcript.jsonl`](../../.acceptance-runs/fedora-44-server-x86_64/20261102T103916Z-test-server-selenium-bindings-lifecycle-68b8d262/transcript.jsonl).
