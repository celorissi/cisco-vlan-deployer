# 2-Planejamento.py
import pandas as pd
import os

INPUT_FILE = "outputs/levantamento.xlsx"
OUTPUT_DIR = "outputs/plan_commands"
VLAN_ID = 14
VLAN_NAME = "DEVEXT"

os.makedirs(OUTPUT_DIR, exist_ok=True)

trunks = pd.read_excel(INPUT_FILE, sheet_name="Trunks")
portchannels = pd.read_excel(INPUT_FILE, sheet_name="PortChannels")

switches = trunks['Hostname'].unique()

for sw in switches:
    commands = [f"vlan {VLAN_ID}", f" name {VLAN_NAME}"]

    sw_trunks = trunks[trunks['Hostname'] == sw]
    for _, row in sw_trunks.iterrows():
        if str(VLAN_ID) not in str(row['Allowed_VLANs']):
            commands.append(f"interface {row['Interface']}")
            commands.append(f" switchport trunk allowed vlan add {VLAN_ID}")

    sw_pos = portchannels[portchannels['Hostname'] == sw]
    for _, row in sw_pos.iterrows():
        commands.append(f"interface Po{row['PortChannel']}")
        commands.append(f" switchport trunk allowed vlan add {VLAN_ID}")

    file_path = os.path.join(OUTPUT_DIR, f"{sw}_commands.txt")
    with open(file_path, "w") as f:
        f.write("\n".join(commands))

print(f"Comandos gerados em: {OUTPUT_DIR}")
