# Visible deferred candidates

These entries are design candidates and have **no executable catalog ID**.

| Candidate | Present finding | Acceptance needed |
| --- | --- | --- |
| Plaso | Upstream documents an opt-in [Fedora COPR path](https://plaso.readthedocs.io/en/latest/sources/user/Fedora-Packaged-Release.html). The legacy function is incomplete. | Review repository trust, signatures, dependencies, installation, observation and removal in supported Fedora VMs before adding a handler. |
| Autopsy | Upstream has [Linux setup instructions](https://github.com/sleuthkit/autopsy/blob/develop/Running_Linux_OSX.md). The legacy function is incomplete. | Verify installer and Java dependency lifecycle, source authenticity, ownership and exact removal in VMs. |
| Firefox policies | The existing helper has merge, block and finalize behavior and unit tests. | Integrate journal ownership and restart-dependent removal before exposing v3 operation. |
| Hexwalk | Sander's active preset includes it. | Verify maintained source and acquisition method before choosing provider. |

`InstallVolatility3` and `RemoveVolatility3` are replaced by the isolated
`package.volatility3` candidate. Only Volatility3 core and its required
`pefile` dependency are pinned; optional plugin dependencies are outside this
operation's claim. The old `RemoveVolatility3` function targets an unrelated
file and is never called by v3.
