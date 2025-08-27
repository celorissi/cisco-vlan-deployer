# 1-Levantamento.py
import pandas as pd
from netmiko import ConnectHandler
import csv
import os
from utils.parsing import parse_cdp, parse_trunks, parse_portchannel

USERNAME = "admin"
PASSWORD = "senhaforte@123"

devices = []
with open("devices.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        devices.append(row)

cdp_data, trunk_data, po_data = [], [], []

for device in devices:
    try:
        conn = ConnectHandler(
            device_type=device["device_type"],
            host=device["ip"],
            username=USERNAME,
            password=PASSWORD
        )
        hostname = conn.find_prompt().replace("#", "")
        platform = device.get("platform", "catalyst")

        cdp_data += [{"Hostname": hostname, "IP": device["ip"], **n} for n in parse_cdp(conn.send_command("show cdp neighbors detail"))]

        trunks = parse_trunks(conn.send_command("show interface trunk"), platform)
        # Pega VLANs atuais direto no show run
        for t in trunks:
            iface = t["Interface"]
            output = conn.send_command(f"show run interface {iface}")
            match = re.search(r"switchport trunk allowed vlan (.+)", output)
            if match:
                t["Allowed_VLANs"] = match.group(1)
            trunk_data.append({"Hostname": hostname, "IP": device["ip"], **t})

        po_data += [{"Hostname": hostname, "IP": device["ip"], **p} for p in parse_portchannel(conn.send_command("show etherchannel summary"))]

        conn.disconnect()
    except Exception as e:
        print(f"Erro em {device['ip']}: {e}")

os.makedirs("outputs", exist_ok=True)
with pd.ExcelWriter("outputs/levantamento.xlsx") as writer:
    pd.DataFrame(cdp_data).to_excel(writer, sheet_name="CDP", index=False)
    pd.DataFrame(trunk_data).to_excel(writer, sheet_name="Trunks", index=False)
    pd.DataFrame(po_data).to_excel(writer, sheet_name="PortChannels", index=False)

print("Levantamento finalizado em outputs/levantamento.xlsx")
