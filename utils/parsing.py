# utils/parsing.py
import re

def parse_cdp(output):
    neighbors = []
    blocks = output.split("-------------------------")
    for block in blocks:
        device_match = re.search(r"Device ID: (\S+)", block)
        local_match = re.search(r"Interface: (\S+),", block)
        port_match = re.search(r"Port ID \(outgoing port\): (\S+)", block)
        if device_match and local_match and port_match:
            neighbors.append({
                "Local_Interface": local_match.group(1),
                "Neighbor": device_match.group(1),
                "Neighbor_Port": port_match.group(1)
            })
    return neighbors

def parse_trunks(output, platform="catalyst"):
    trunks = []
    iface_regex = re.compile(r'^(Po\d+|Gi\d+/\d+(/\d+)?|Fa\d+/\d+(/\d+)?|Te\d+/\d+(/\d+)?)$')
    lines = output.splitlines()
    section = None
    vlan_allowed = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if platform == "catalyst":
            if line.startswith("Port") and "Mode" in line and "Status" in line:
                section = "main"
                continue
            elif line.startswith("Port Vlans allowed on trunk"):
                section = "allowed"
                continue
            elif line.startswith("Port Vlans allowed and active") or line.startswith("Port Vlans in spanning tree"):
                section = None
                continue
        elif platform == "nexus":
            if line.startswith("Port") and "Mode" in line and "Status" in line:
                section = "main"
                continue
            elif line.startswith("Trunking VLANs Allowed"):
                section = "allowed"
                continue

        if section == "main":
            parts = line.split()
            if len(parts) >= 5 and iface_regex.match(parts[0]):
                trunks.append({
                    "Interface": parts[0],
                    "Mode": parts[1],
                    "Encapsulation": parts[2],
                    "Status": parts[3],
                    "Native_VLAN": parts[4],
                    "Allowed_VLANs": ""
                })

        elif section == "allowed":
            parts = line.split()
            if len(parts) >= 2 and iface_regex.match(parts[0]):
                iface = parts[0]
                vlans = " ".join(parts[1:])
                vlan_allowed[iface] = vlans

    for trunk in trunks:
        iface = trunk["Interface"]
        if iface in vlan_allowed:
            trunk["Allowed_VLANs"] = vlan_allowed[iface]

    return trunks

def parse_portchannel(output):
    portchannels = []
    lines = output.splitlines()
    for line in lines:
        if re.match(r"^\d+\s", line):
            parts = line.split()
            po = parts[0]
            protocol = parts[1]
            status = parts[2]
            members = " ".join(parts[3:])
            portchannels.append({
                "PortChannel": po,
                "Protocol": protocol,
                "Status": status,
                "Members": members
            })
    return portchannels
