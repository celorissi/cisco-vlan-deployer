# Cisco VLAN Deployer

Automação para criação de VLANs em ambientes Cisco Catalyst, com análise de trunks e port-channels.  
Permite inventariar switches, planejar comandos de configuração e aplicar novas VLANs de forma segura.

---

## Estrutura do Repositório

| Arquivo/Pasta            | Descrição                                            |
|--------------------------|------------------------------------------------------|
| 1-Levantamento.py        | Coleta inventário: CDP, trunks, port-channels        |
| 2-Planejamento.py        | Analisa e gera comandos para criar VLAN              |
| 3-Configuracao.py        | Aplica comandos em switches selecionados             |
| 4-Rollback.py            | Remove VLANs em switches selecionados (rollback).    |
| devices.csv              | Inventário de switches                               |
| outputs/                 | Saída dos Excel e arquivos de comando                |
| README.md                | Documentação do projeto                              |
| utils/                   | Pasta com scripts utilitários                        |
| utils/parsing.py         | Funções de parsing compartilhadas                    |

---

## Pré-requisitos

- Python 3.9 ou superior  
- Bibliotecas Python:
  - `pandas`
  - `netmiko`
  - `openpyxl` (>= 3.1.0)

Instalação rápida:

```bash
pip install pandas netmiko openpyxl
```

- Acesso SSH aos switches Cisco, com usuário e senha configurados no script.

---

## Como usar

### 1. Levantamento

Coleta informações de CDP, trunks e port-channels de todos os switches listados no `devices.csv`.

```bash
python 1-Levantamento.py
```

Saída: `outputs/levantamento.xlsx` com abas:

- **CDP** – vizinhança entre switches e APs  
- **Trunks** – interfaces trunk, VLAN nativa e VLANs permitidas  
- **PortChannels** – status e membros de cada trunk lógico

> O script **não faz alterações nos switches**.

---

### 2. Planejamento

Analisa a saída do levantamento e gera comandos para adicionar uma VLAN nos trunks e port-channels.

```bash
python 2-Planejamento.py
```

- Escolha `VLAN_ID` e `VLAN_NAME` quando solicitado.  
- Arquivos de comando gerados por switch em: `outputs/plan_commands/`

> O script **não aplica nenhuma configuração**, apenas gera os comandos.

---

### 3. Configuração

Aplica os comandos de VLAN em switches específicos ou em todos.

```bash
python 3-Configuracao.py
```

- Permite selecionar quais switches serão configurados.  
- Mostra **preview dos comandos** antes da aplicação.  
- Cria logs de execução em `outputs/`.

---

### 4. Rollback
python 4-Rollback.py


Permite escolher o switch pelo menu.

Remove a VLAN selecionada apenas das interfaces que possuem a VLAN e ignorando interfaces críticas ( mgmt, loopback).

Salva log em outputs/rollback_logs/.

---

## Boas práticas

- Rodar os scripts em ordem: **1 → 2 → 3**.  
- Sempre revisar os comandos no passo 2 antes de aplicar no passo 3.  
- Para ambientes críticos, execute **primeiro em um switch isolado**.  
- Interfaces de APs ou equipamentos de terceiros (ex.: `axis-xxxx`) são automaticamente ignoradas pelo script.  

---

## Licença

Projeto público para aprendizado e uso corporativo.  

---

## Contato

Desenvolvido por **Marcelo**, especialista em redes e automação Cisco.  
Para dúvidas ou sugestões: LinkedIn ou GitHub.