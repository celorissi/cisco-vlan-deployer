import pandas as pd
from netmiko import ConnectHandler
import os
import re
import getpass

# ===== Configurações =====
DEVICES_FILE = "devices.csv"
LEVANTAMENTO_FILE = "outputs/levantamento_switches.xlsx"
OUTPUT_LOG_DIR = "outputs/rollback_logs"

os.makedirs(OUTPUT_LOG_DIR, exist_ok=True)

# ===== Credenciais =====
username = input("Digite o usuário de acesso: ").strip()
password = getpass.getpass("Digite a senha: ").strip()

# ===== Lê dados =====
devices_df = pd.read_csv(DEVICES_FILE)
trunks_df = pd.read_excel(LEVANTAMENTO_FILE, sheet_name="Trunks")

# Lista switches disponíveis
switches = trunks_df['Hostname'].unique().tolist()
print("Switches disponíveis:")
for i, sw in enumerate(switches, start=1):
    ip = devices_df.loc[devices_df['Hostname'] == sw, 'IP'].values[0]
    print(f"{i}. {sw} ({ip})")

choice_input = input("Escolha o switch para rollback (digite número ou hostname): ").strip()

# Seleção por número ou hostname
try:
    choice_index = int(choice_input) - 1
    if choice_index < 0 or choice_index >= len(switches):
        raise ValueError
    chosen_switch = switches[choice_index]
except ValueError:
    if choice_input not in switches:
        print("Switch inválido.")
        exit()
    chosen_switch = choice_input

# Obtem IP do CSV automaticamente
ip = devices_df.loc[devices_df['Hostname'] == chosen_switch, 'IP'].values[0]

# Pergunta VLAN a ser removida
vlan_id = input("Digite o VLAN_ID que deseja remover: ").strip()

# ===== Filtra trunks do switch escolhido =====
switch_trunks = trunks_df[trunks_df['Hostname'] == chosen_switch]

# Comandos globais e por interface
rollback_commands_global = [f"no vlan {vlan_id}"]
rollback_commands_interfaces = []

for _, row in switch_trunks.iterrows():
    iface = row['Interface']
    allowed_vlans = str(row['Allowed_VLANs'])
    # Ignora interfaces críticas
    if re.match(r'(axis-|mgmt|loopback)', iface, re.IGNORECASE):
        continue
    # Se VLAN está na interface, adiciona comando
    if vlan_id in allowed_vlans.replace(" ", "").split(","):
        rollback_commands_interfaces.append(f"interface {iface}")
        rollback_commands_interfaces.append(f" switchport trunk allowed vlan remove {vlan_id}")

# Preview
print("\nComandos que serão aplicados no rollback:")
for cmd in rollback_commands_global + rollback_commands_interfaces:
    print(cmd)

confirm = input("\nDeseja aplicar o rollback? (y/n): ").strip().lower()
if confirm != "y":
    print("Rollback cancelado.")
    exit()

# ===== Conexão e aplicação =====
device_info = {
    "device_type": "cisco_ios",
    "host": ip,
    "username": username,
    "password": password
}

try:
    conn = ConnectHandler(**device_info)
    output_log = ""

    # Aplica comandos globais
    if rollback_commands_global:
        output_log += conn.send_config_set(rollback_commands_global) + "\n"

    # Aplica comandos por interface em blocos
    i = 0
    while i < len(rollback_commands_interfaces):
        if rollback_commands_interfaces[i].startswith("interface"):
            iface_block = [rollback_commands_interfaces[i]]
            i += 1
            # adiciona comandos switchport abaixo
            while i < len(rollback_commands_interfaces) and rollback_commands_interfaces[i].startswith(" switchport"):
                iface_block.append(rollback_commands_interfaces[i])
                i += 1
            # envia bloco
            output_log += conn.send_config_set(iface_block) + "\n"
        else:
            i += 1

    conn.disconnect()

    # ===== Salva log =====
    log_file = os.path.join(OUTPUT_LOG_DIR, f"{chosen_switch}_rollback.log")
    with open(log_file, "w") as f:
        f.write(output_log)

    print(f"\nRollback aplicado com sucesso. Log salvo em: {log_file}")

except Exception as e:
    print(f"Erro ao conectar ou aplicar comandos no switch {chosen_switch}: {e}")
