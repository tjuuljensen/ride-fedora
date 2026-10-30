"""Disposable QEMU guest for RIDE's cross-distro acceptance contract.

The host owns VM creation and SSH transport. Test assertions stay independent
of the guest's package manager; target-specific observations belong in tests.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import subprocess
import tarfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "tests" / "acceptance" / "targets.json"
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SOURCE_PATHS = ("ride.sh", "catalog", "profiles", "lib/v3", "requirements")


def load_target(target_id: str, matrix_path: Path = TARGETS) -> dict[str, Any]:
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if matrix.get("schemaVersion") != 1 or not isinstance(matrix.get("targets"), list):
        raise ValueError("invalid VM target matrix")
    seen: set[str] = set()
    selected = None
    for target in matrix["targets"]:
        if not isinstance(target, dict) or any(
            not isinstance(target.get(key), str) or not target[key]
            for key in ("id", "distro", "release", "edition", "variantId", "architecture",
                        "imageFormat", "imageSha256", "imageSource", "imageRelease",
                        "acceptanceScope", "pilotOperation", "pilotPackage",
                        "packageDatabase", "packageVerification")
        ):
            raise ValueError("invalid VM target entry")
        if not ID_PATTERN.fullmatch(target["id"]) or target["id"] in seen:
            raise ValueError("invalid or duplicate VM target ID")
        if not re.fullmatch(r"[a-z0-9-]+", target["variantId"]):
            raise ValueError("invalid VM edition variant ID")
        if target["imageFormat"] != "qcow2" or not SHA256_PATTERN.fullmatch(target["imageSha256"]):
            raise ValueError("VM target needs a qcow2 image and SHA256 digest")
        if not re.fullmatch(r"package\.[a-z0-9.-]+", target["pilotOperation"]):
            raise ValueError("invalid VM pilot operation")
        if not re.fullmatch(r"[A-Za-z0-9+_.-]+", target["pilotPackage"]):
            raise ValueError("invalid VM pilot package")
        additional = target.get("additionalPilots", [])
        if not isinstance(additional, list):
            raise ValueError("invalid additional VM pilots")
        pilot_ids = {target["pilotOperation"]}
        for pilot in additional:
            if (not isinstance(pilot, dict) or
                    not isinstance(pilot.get("operationId"), str) or
                    not re.fullmatch(r"package\.[a-z0-9.-]+", pilot["operationId"]) or
                    not isinstance(pilot.get("package"), str) or
                    not re.fullmatch(r"[A-Za-z0-9+_.-]+", pilot["package"]) or
                    pilot["operationId"] in pilot_ids):
                raise ValueError("invalid or duplicate additional VM pilot")
            pilot_ids.add(pilot["operationId"])
        if target["packageDatabase"] not in ("rpm", "dpkg"):
            raise ValueError("unknown VM package database")
        if target["packageVerification"] not in ("rpm-signature-and-files", "apt-repository"):
            raise ValueError("unknown VM package verification")
        if (target["packageDatabase"], target["packageVerification"]) not in (
            ("rpm", "rpm-signature-and-files"), ("dpkg", "apt-repository")
        ):
            raise ValueError("VM package database and verification do not match")
        seed_packages = target.get("seedPackages", ["jq", "sudo"])
        if not isinstance(seed_packages, list) or any(
            not isinstance(package, str) or not re.fullmatch(r"[A-Za-z0-9+_.-]+", package)
            for package in seed_packages
        ):
            raise ValueError("invalid VM seed package list")
        seen.add(target["id"])
        if target["id"] == target_id:
            selected = target
    if selected is None:
        raise ValueError(f"unknown VM target: {target_id}")
    return selected


def select_pilot(target: dict[str, Any], operation_id: str | None) -> dict[str, Any]:
    if operation_id is None or operation_id == target["pilotOperation"]:
        return target
    for pilot in target.get("additionalPilots", []):
        if pilot["operationId"] == operation_id:
            selected = target.copy()
            selected["pilotOperation"] = operation_id
            selected["pilotPackage"] = pilot["package"]
            return selected
    raise ValueError(f"pilot operation is not declared for {target['id']}: {operation_id}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_image(path: Path, target: dict[str, str]) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"image must be a regular, non-symlink file: {path}")
    actual = file_sha256(path)
    if actual != target["imageSha256"]:
        raise ValueError(f"image SHA256 mismatch: expected {target['imageSha256']}, got {actual}")
    info = subprocess.run(
        ["qemu-img", "info", "--output=json", str(path)],
        text=True, capture_output=True, check=True, timeout=30,
    )
    if json.loads(info.stdout).get("format") != "qcow2":
        raise ValueError("image is not qcow2")
    return actual


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def qemu_command(overlay: Path, seed: Path, serial: Path, port: int,
                 *, accel: str = "kvm") -> list[str]:
    if not 1 <= port <= 65535:
        raise ValueError("invalid SSH forward port")
    if accel not in {"kvm", "tcg"}:
        raise ValueError("unsupported QEMU acceleration mode")
    return [
        "qemu-system-x86_64", "-accel", accel, "-machine", "q35",
        "-cpu", "host" if accel == "kvm" else "max",
        "-smp", "2", "-m", "3072", "-display", "none", "-monitor", "none",
        "-serial", f"file:{serial}",
        "-drive", f"file={overlay},if=virtio,format=qcow2",
        "-drive", f"file={seed},media=cdrom,readonly=on",
        "-netdev", f"user,id=net0,hostfwd=tcp:127.0.0.1:{port}-:22",
        "-device", "virtio-net-pci,netdev=net0",
    ]


def assert_guest_target(os_release: str, architecture: str,
                        target: dict[str, str]) -> None:
    values = dict(line.split("=", 1) for line in os_release.splitlines() if "=" in line)
    actual = tuple(values.get(key, "").strip('"') for key in ("ID", "VERSION_ID", "VARIANT_ID"))
    actual += (architecture.strip(),)
    expected = tuple(target[key] for key in ("distro", "release", "variantId", "architecture"))
    if actual != expected:
        raise AssertionError(f"guest target mismatch: {actual}, expected {expected}")


class VM:
    """One isolated scenario, always created from a clean verified base image."""

    def __init__(self, target: dict[str, str], image: Path, artifacts: Path,
                 *, accel: str = "kvm"):
        if accel not in {"kvm", "tcg"}:
            raise ValueError("unsupported QEMU acceleration mode")
        self.target = target
        self.image = image.resolve()
        self.artifacts = artifacts.resolve()
        self.accel = accel
        for source in SOURCE_PATHS[1:]:
            if self.artifacts.is_relative_to(ROOT / source):
                raise ValueError("VM output cannot be inside bundled source directories")
        if self.artifacts.is_relative_to(ROOT / "docs" / "acceptance"):
            raise ValueError("VM output cannot be inside bundled acceptance documents")
        self.key = self.artifacts / "ssh_key"
        self.port = 0
        self.process: subprocess.Popen[bytes] | None = None
        self._qemu_log = None
        self.repo = "/home/ride-test/ride"

    def _record(self, event: dict[str, Any]) -> None:
        with (self.artifacts / "transcript.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True) + "\n")

    def _command(self, command: list[str], *, timeout: int = 120,
                 check: bool = True, record: bool = True) -> subprocess.CompletedProcess[str]:
        started = time.monotonic()
        try:
            result = subprocess.run(command, text=True, capture_output=True,
                                    timeout=timeout, check=False)
        except subprocess.TimeoutExpired as error:
            if record:
                self._record({"command": command, "timedOut": True, "timeoutSeconds": timeout,
                              "stdout": error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else error.stdout,
                              "stderr": error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else error.stderr})
            raise
        if record:
            self._record({"command": command, "exitCode": result.returncode,
                          "elapsedSeconds": round(time.monotonic() - started, 2),
                          "stdout": result.stdout, "stderr": result.stderr})
        if check and result.returncode != 0:
            raise AssertionError(f"command failed ({result.returncode}): {command}\n{result.stdout}\n{result.stderr}")
        return result

    def _ssh_options(self) -> list[str]:
        return ["-i", str(self.key), "-o", "IdentitiesOnly=yes",
                "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=accept-new",
                "-o", f"UserKnownHostsFile={self.artifacts / 'known_hosts'}"]

    def run(self, script: str, *, timeout: int = 120,
            check: bool = True) -> subprocess.CompletedProcess[str]:
        command = ["ssh", *self._ssh_options(), "-p", str(self.port),
                   "ride-test@127.0.0.1", f"bash -lc {shlex.quote(script)}"]
        return self._command(command, timeout=timeout, check=check)

    def ride(self, *args: str, catalog: str | None = None, timeout: int = 120,
             check: bool = True) -> subprocess.CompletedProcess[str]:
        prefix = "sudo "
        if catalog is not None:
            prefix += f"env RIDE_CATALOG_PATH={shlex.quote(catalog)} "
        script = prefix + shlex.join([f"{self.repo}/ride.sh", *args])
        return self.run(script, timeout=timeout, check=check)

    def put_json(self, name: str, value: dict[str, Any]) -> str:
        if not ID_PATTERN.fullmatch(name):
            raise ValueError("invalid guest fixture name")
        local = self.artifacts / f"{name}.json"
        local.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        guest = f"/home/ride-test/{name}.json"
        self._command(["scp", *self._ssh_options(), "-P", str(self.port),
                       str(local), f"ride-test@127.0.0.1:{guest}"], timeout=60)
        return guest

    def _seed(self) -> Path:
        self._command(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(self.key)],
                      timeout=30, record=False)
        public_key = self.key.with_suffix(".pub").read_text(encoding="ascii").strip()
        if not re.fullmatch(r"ssh-ed25519 [A-Za-z0-9+/=]+(?: [^\n]*)?", public_key):
            raise ValueError("unexpected generated SSH public key")
        user_data = self.artifacts / "user-data"
        cloud_config = (
            "#cloud-config\n"
            "preserve_hostname: true\n"
            "users:\n"
            "  - name: ride-test\n"
            "    sudo: ALL=(ALL) NOPASSWD:ALL\n"
            "    lock_passwd: true\n"
            "    ssh_authorized_keys:\n"
            f"      - {public_key}\n"
            "ssh_pwauth: false\n"
            "disable_root: true\n"
        )
        seed_packages = self.target.get("seedPackages", ["jq", "sudo"])
        if seed_packages:
            cloud_config += f"packages: [{', '.join(seed_packages)}]\n"
        user_data.write_text(cloud_config, encoding="utf-8")
        meta_data = self.artifacts / "meta-data"
        meta_data.write_text(
            f"instance-id: ride-{self.artifacts.name}\n",
            encoding="utf-8",
        )
        seed = self.artifacts / "seed.iso"
        self._command(["genisoimage", "-quiet", "-output", str(seed), "-volid", "CIDATA",
                       "-joliet", "-rock", str(user_data), str(meta_data)], timeout=30)
        return seed

    def _bundle(self) -> Path:
        bundle = self.artifacts / "ride.tar.gz"
        with tarfile.open(bundle, "w:gz") as archive:
            for source in SOURCE_PATHS:
                path = ROOT / source
                members = (path,) if path.is_file() else sorted(path.rglob("*"))
                for member in members:
                    if (not member.is_file() or member.is_symlink() or
                            "__pycache__" in member.parts or member.suffix == ".pyc"):
                        continue
                    archive.add(member, arcname=f"ride/{member.relative_to(ROOT)}")
            for member in sorted((ROOT / "docs" / "acceptance").glob("*.md")):
                if member.is_file() and not member.is_symlink():
                    archive.add(member, arcname=f"ride/{member.relative_to(ROOT)}")
        return bundle

    def _wait_for_ssh(self, timeout: int = 600) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.process is not None and self.process.poll() is not None:
                raise RuntimeError(f"QEMU stopped during boot; inspect {self.artifacts / 'qemu.log'}")
            result = self._command(
                ["ssh", *self._ssh_options(), "-p", str(self.port),
                 "ride-test@127.0.0.1", "true"], timeout=10, check=False, record=False)
            if result.returncode == 0:
                return
            time.sleep(3)
        raise TimeoutError(f"SSH did not become ready; inspect {self.artifacts / 'serial.log'}")

    def start(self) -> None:
        if self.target["architecture"] != "x86_64":
            raise ValueError("this QEMU launcher currently supports x86_64 guests only")
        if os.uname().machine != "x86_64":
            raise RuntimeError("x86_64 host is required for VM acceptance")
        if self.accel == "kvm" and not os.access("/dev/kvm", os.R_OK | os.W_OK):
            raise RuntimeError("x86_64 KVM access is required for VM acceptance")
        for program in ("qemu-img", "qemu-system-x86_64", "genisoimage", "ssh-keygen", "ssh", "scp", "git"):
            if shutil.which(program) is None:
                raise RuntimeError(f"missing VM harness prerequisite: {program}")
        self.artifacts.mkdir(mode=0o700, parents=True, exist_ok=False)
        digest = verify_image(self.image, self.target)
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                  capture_output=True, check=True, timeout=10).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True,
                                    capture_output=True, check=True, timeout=10).stdout)
        metadata = {"target": self.target, "imagePath": str(self.image),
                    "acceleration": self.accel,
                    "verifiedImageSha256": digest, "sourceRevision": revision,
                    "sourceHasUncommittedChanges": dirty,
                    "catalogSha256": file_sha256(ROOT / "catalog" / "operations.json")}
        (self.artifacts / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self._record(metadata)
        overlay = self.artifacts / "overlay.qcow2"
        self._command(["qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
                       "-b", str(self.image), str(overlay)], timeout=30)
        seed = self._seed()
        self.port = free_loopback_port()
        self._qemu_log = (self.artifacts / "qemu.log").open("wb")
        self.process = subprocess.Popen(
            qemu_command(overlay, seed, self.artifacts / "serial.log", self.port,
                         accel=self.accel),
            stdin=subprocess.DEVNULL, stdout=self._qemu_log, stderr=subprocess.STDOUT,
        )
        try:
            self._wait_for_ssh(timeout=1800 if self.accel == "tcg" else 600)
            self.run("cloud-init status --wait", timeout=1800 if self.accel == "tcg" else 600)
            self.run("command -v bash && command -v jq && command -v sudo")
            os_release = self.run("cat /etc/os-release").stdout
            arch = self.run("uname -m").stdout.strip()
            assert_guest_target(os_release, arch, self.target)
            bundle = self._bundle()
            bundle_digest = file_sha256(bundle)
            metadata_path = self.artifacts / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["sourceBundleSha256"] = bundle_digest
            metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
            self._record({"sourceBundleSha256": bundle_digest})
            self._command(["scp", *self._ssh_options(), "-P", str(self.port), str(bundle),
                           "ride-test@127.0.0.1:/home/ride-test/ride.tar.gz"], timeout=120)
            self.run("tar -xzf /home/ride-test/ride.tar.gz -C /home/ride-test")
            self.ride("--version")
        except BaseException:
            self.stop()
            raise

    def stop(self) -> None:
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=10)
            self.process = None
        if self._qemu_log is not None:
            self._qemu_log.close()
            self._qemu_log = None
