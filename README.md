````markdown
# 🪐 Júpiter – Sistema de Coleta, Logística e Visualização de Dados

O **Júpiter** é um sistema automatizado que integra **dados de rastreadores** e **planilhas de logística** para gerar **painéis visuais e interativos**. Criado para facilitar o acompanhamento de dispositivos e envios em larga escala, ele transforma informações operacionais em interfaces claras e úteis para tomada de decisão.

---

## ⚙️ O que o Júpiter faz

- 🔌 **Consome dados da API da TopFly**, coletando diariamente a **última localização dos dispositivos**, registrada por volta das **2h da manhã da noite anterior**.
- 🗺️ Exibe um **mapa em nível nacional** com a posição de todos os dispositivos, facilitando a visualização geográfica da frota.
- 📊 **Atualiza painéis interativos** com base nos dados coletados, otimizando o monitoramento da operação.
- 📦 **Integra com planilhas do Google (via API)**, transformando automaticamente as informações de envio dos Correios em um **painel logístico visual e intuitivo**.
- 🔁 Automatiza a sincronização de dados com os painéis públicos ou privados do projeto.
- ✅ Fornece um **script `.bat`** para execução automatizada em ambientes Windows com apenas um clique.

---

## 🗂️ Estrutura do Projeto

| Arquivo          | Função                                                                 |
|------------------|------------------------------------------------------------------------|
| `consulta.py`    | Coleta dados dos dispositivos via API da TopFly e gera `devices_data.json`. |
| `commit.py`      | Atualiza o painel de dispositivos com os dados coletados.              |
| `logistica.py`   | Lê dados de uma planilha Google (via API) com informações de envios.   |
| `commit2.py`     | Gera e publica o painel visual da logística.                           |
| `rodar_jupiter.bat` | Script automatizado para rodar todas as etapas com um clique.        |

---

## 📦 Logística Inteligente

A parte logística do Júpiter conecta-se diretamente a uma **planilha do Google com dados de envio dos Correios** (códigos de rastreio, destinatários, status etc.). Com isso, o sistema:

- Atualiza automaticamente os dados da planilha;
- Gera visualizações que facilitam o acompanhamento de entregas;
- Exibe status organizados em tempo real;
- Centraliza todas as informações em um único painel visual.

---

## 🗺️ Visualização Geográfica

O painel de dispositivos inclui um **mapa do Brasil** com a última localização conhecida de cada rastreador, permitindo:

- Visualização geográfica da frota;
- Detecção de inatividade ou dispersão dos dispositivos;
- Controle de presença por região.

---

## ✅ Requisitos

- Python 3.10 ou superior  
- Git  
- Biblioteca: `requests`  
- Acesso autorizado à planilha do Google (com API Sheets habilitada)  
- Chave de acesso válida para a API da TopFly

---

## 🚀 Como executar (Windows)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/headdira/jupiter
   cd jupiter
````

2. **Instale a dependência:**

   ```bash
   pip install requests
   ```

3. **Execute o script automático:**

   ```bash
   rodar_jupiter.bat
   ```

---

## 📁 Ambiente Linux/macOS

Você pode executar os scripts manualmente com:

```bash
python consulta.py
python commit.py
python logistica.py
python commit2.py
```

*(Ainda não há um `.sh` automatizado, mas posso ajudar a criar.)*

---

## 🛡️ Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.

## 📬 Contato

Em caso de dúvidas técnicas ou colaboração, entre em contato com a equipe responsável pelo projeto.

---

```
