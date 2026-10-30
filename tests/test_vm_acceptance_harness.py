"""Host-side checks for VM matrix and image safety gates."""

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.vm_acceptance import (VM, ROOT, assert_guest_target, load_target,
                                 qemu_command, select_pilot, verify_image)


class VmHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = {
            "id": "fedora-44-cloud-x86_64", "distro": "fedora", "release": "44",
            "edition": "Cloud Base", "variantId": "cloud", "architecture": "x86_64", "imageFormat": "qcow2",
            "imageSha256": "3a6eb0790f39ac87c94f3856b2dd2c5d110e6811602261a9a923d3bb23adc8b7",
            "imageSource": "https://fedoraproject.org/cloud/download/",
            "imageRelease": "44-1.7", "acceptanceScope": "generic-package-pilot",
            "pilotOperation": "package.exfatprogs", "pilotPackage": "exfatprogs",
            "packageDatabase": "rpm", "packageVerification": "rpm-signature-and-files",
        }

    def test_target_matrix_rejects_duplicate_and_unknown_ids(self):
        self.assertEqual(load_target("fedora-44-cloud-x86_64")["pilotOperation"],
                         "package.exfatprogs")
        matrix = self.root / "targets.json"
        matrix.write_text(json.dumps({"schemaVersion": 1, "targets": [self.target]}))
        self.assertEqual(load_target(self.target["id"], matrix), self.target)
        with self.assertRaisesRegex(ValueError, "unknown VM target"):
            load_target("ubuntu-99", matrix)
        matrix.write_text(json.dumps({"schemaVersion": 1, "targets": [self.target, self.target]}))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_target(self.target["id"], matrix)

    def test_image_digest_and_format_are_both_checked(self):
        image = self.root / "image.qcow2"
        image.write_bytes(b"image")
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            verify_image(image, self.target)
        self.target["imageSha256"] = hashlib.sha256(b"image").hexdigest()
        with patch("tools.vm_acceptance.subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout='{"format":"raw"}', stderr=""
        )):
            with self.assertRaisesRegex(ValueError, "not qcow2"):
                verify_image(image, self.target)

    def test_guest_edition_must_match_the_pinned_target(self):
        os_release = 'ID=fedora\nVERSION_ID=44\nVARIANT_ID=cloud\n'
        assert_guest_target(os_release, 'x86_64', self.target)
        with self.assertRaisesRegex(AssertionError, 'guest target mismatch'):
            assert_guest_target(os_release.replace('cloud', 'workstation'), 'x86_64', self.target)

    def test_only_declared_pilot_can_be_selected(self):
        target = load_target("fedora-44-workstation-x86_64")
        selected = select_pilot(target, "package.less")
        self.assertEqual((selected["pilotOperation"], selected["pilotPackage"]),
                         ("package.less", "less"))
        self.assertEqual(select_pilot(target, "package.openssh-clients")["pilotPackage"],
                         "openssh-clients")
        self.assertEqual(target["pilotOperation"], "package.exfatprogs")
        with self.assertRaisesRegex(ValueError, "not declared"):
            select_pilot(target, "package.unknown")

    def test_qemu_ssh_forward_is_loopback_only(self):
        command = qemu_command(self.root / "overlay.qcow2", self.root / "seed.iso",
                               self.root / "serial.log", 2222)
        self.assertIn("user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22", command)
        software = qemu_command(self.root / "overlay.qcow2", self.root / "seed.iso",
                                self.root / "serial.log", 2222, accel="tcg")
        self.assertEqual(software[1:3], ["-accel", "tcg"])
        self.assertEqual(software[5:7], ["-cpu", "max"])
        self.assertIn("user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22", software)
        with self.assertRaises(ValueError):
            qemu_command(self.root / "overlay.qcow2", self.root / "seed.iso",
                         self.root / "serial.log", 0)
        with self.assertRaises(ValueError):
            qemu_command(self.root / "overlay.qcow2", self.root / "seed.iso",
                         self.root / "serial.log", 2222, accel="unknown")

    def test_output_cannot_be_nested_inside_the_source_bundle(self):
        with self.assertRaisesRegex(ValueError, "VM output cannot be inside"):
            VM(self.target, self.root / "image.qcow2", ROOT / "catalog" / "run")


if __name__ == "__main__":
    unittest.main()
