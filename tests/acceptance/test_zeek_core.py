"""Focused offline smoke for the Fedora Zeek CLI replacement path."""

def test_zeek_reads_a_synthetic_offline_capture(vm):
    vm.run("sudo dnf install -y zeek-core", timeout=1200)
    vm.run(
        "work=$(mktemp -d /home/ride-test/zeek-smoke.XXXXXX); "
        "trap 'rm -rf -- \"$work\"' EXIT; "
        "python3 - \"$work/synthetic.pcap\" <<'PY'\n"
        "import socket, struct, sys\n"
        "ethernet = bytes(12) + b'\\x08\\x00'\n"
        "ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 40, 1, 0, 64, 6, 0, socket.inet_aton('192.0.2.1'), socket.inet_aton('192.0.2.2'))\n"
        "tcp = struct.pack('!HHIIHHHH', 12345, 80, 1, 0, (5 << 12) | 2, 64240, 0, 0)\n"
        "packet = ethernet + ip + tcp\n"
        "with open(sys.argv[1], 'wb') as capture:\n"
        "    capture.write(struct.pack('<IHHIIII', 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))\n"
        "    capture.write(struct.pack('<IIII', 1, 0, len(packet), len(packet)) + packet)\n"
        "PY\n"
        "cd \"$work\" && zeek -C -r synthetic.pcap && test -s conn.log"
    )
