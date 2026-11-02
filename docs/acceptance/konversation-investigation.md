# Konversation successor investigation

Decision: do not expose Konversation as a Fedora 44 v3 operation. Its signed
Fedora 44 RPM installed, but `konversation --version` failed to start because
`libKF6Codecs.so.6` requires `GLIBCXX_3.4.35`, which the pinned image's
`libstdc++` does not provide. The package transaction upgraded ten existing
RPMs and installed 76 dependencies. This is not a supported or operable path.

The failed disposable VM overlay was removed after the package mismatch was
confirmed. Its transcript is retained at
`/tmp/ride-fedora-native-rpm-03-konversation-final/fedora-44-workstation-x86_64/20261031T082811Z-test-native-konversation-candidate-lifecycle-a2f1fbe7/transcript.jsonl`.
The apply run was `20261031T083104Z-2816-19143`; the test stopped at the
launcher probe before repeat or restore. No IRC account or profile data was
opened. The VM was disposable.

The [Fedora package record](https://packages.fedoraproject.org/pkgs/konversation/konversation/fedora-44-updates.html)
remains the source and license reference. Reconsider this package only after
Fedora's runtime dependency set provides the missing symbol on the pinned
target. Use the GNOME Polari alternative for the current migration path.
