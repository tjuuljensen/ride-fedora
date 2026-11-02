# Polari successor investigation

Decision: do not expose Fedora Polari as a v3 operation on the pinned Fedora
44 Workstation target. The signed `polari` 50.0 RPM installed with six new
packages and no existing RPM upgrades, but `polari --version` exited 1 after
printing `Polari 50.0`. Its GNOME JavaScript then failed with
`TypeError: Utils.getSparqlStore().close is not a function`. The candidate
profile was removed and no IRC account or profile data was opened.

Transcript: `/tmp/ride-fedora-native-rpm-03-polari/fedora-44-workstation-x86_64/20261031T083807Z-test-native-polari-candidate-lifecycle-a52caaf2/transcript.jsonl`.
The apply run was `20261031T084058Z-2809-8434`; the test stopped at the app
startup probe before repeat or restore. The test VM was disposable.

The current [Fedora package record](https://packages.fedoraproject.org/pkgs/polari/polari/)
lists version 50.0 and license `GPL-2.0-or-later AND LGPL-2.0-or-later AND
CC0-1.0`; the [GNOME app page](https://apps.gnome.org/en/Polari/) describes
the client as supporting channel chat and private conversations. Reconsider
the RPM after the upstream runtime API mismatch is corrected on Fedora 44.
