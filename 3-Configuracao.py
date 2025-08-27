# 3-Configuracao.py
from netmiko import ConnectHandler
import os
import csv

USERNAME = "admin"
PASSWORD = "senhaforte@123"
INPUT_DIR = "outputs/plan_commands"
DEVICES_CSV = "devices.csv"
LOG_DIR = "outputs/logs"

os.makedirs(LOG_DIR, exist_ok=True)

hostname_ip_map = {}
with open(DEVICES_CSV) as f:
    reader = csv.DictReader(f)
    for row in reader:
        hostname_ip_map[row['Hostname']] = row.get('IP') or row.get('ip')

files = [f for f in os.listdir(INPUT_DIR) if f.endswith("_commands.txt")]

def listar_switches():
    return [f.split("_commands.txt")[0] for f in files]

def aplicar_comandos(sw_name):
    file_path = os.path.join(INPUT_DIR, f"{sw_name}_commands.txt")
    if not os.path.exists(file_path):
        print(f"Arquivo de comandos para {sw_name} não encontrado!")
        return

    ip = hostname_ip_map.get(sw_name)
    if not ip:
        print(f"IP do switch {sw_name} não encontrado no CSV!")
        return

    with open(file_path) as f:
        commands = [line.strip() for line in f if line.strip()]

    print(f"\nPreview dos comandos para {sw_name} ({ip}):")
    print("-" * 50)
    for cmd in commands:
        print(cmd)
    print("-" * 50)

    confirm = input("Deseja aplicar esses comandos? (s/n): ").strip().lower()
    if confirm != "s":
        print(f"Comandos de {sw_name} não aplicados.\n")
        return

    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        print(f"\nConectando em {sw_name} ({ip})...")
        conn = ConnectHandler(**device)
        output = conn.send_config_set(commands)
        print(f"Comandos aplicados em {sw_name}.")

        log_file = os.path.join(LOG_DIR, f"apply_{sw_name}.log")
        with open(log_file, "w") as f:
            f.write(output)
        print(f"Log salvo em: {log_file}\n")

        conn.disconnect()
    except Exception as e:
        print(f"Erro em {sw_name} ({ip}): {e}")

switches = listar_switches()
print("Switches disponíveis:")
for sw in switches:
    print(f" - {sw}")

choice = input("\nDigite o hostname do switch ou 'all' para todos: ").strip()

if choice.lower() == "all":
    for sw in switches:
        aplicar_comandos(sw)
else:
    if choice in switches:
        aplicar_comandos(choice)
    else:
        print(f"Switch {choice} não encontrado na lista de comandos.")
