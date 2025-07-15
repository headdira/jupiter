import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sqlite3
import os
import json
from datetime import datetime

# Configurações
DB_PATH = "data/logistics_data.sqlite"
DEVICES_JSON_PATH = "data/devices_data.json"
ENRICHED_JSON_PATH = "data/enriched_devices_data.json"
SHEET_KEY = "1i8YPGO-qbdTnkHOrcR4JDHtAdGzARKnCNU6lkyn-lM0"
SHEET_GID = "1417212747"  # GID da aba "todos os envios"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS_FILE = 'credentials.json'  # Arquivo de credenciais do Google API

def setup_database():
    """Cria o banco de dados e tabelas necessárias"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Tabela para controle de atualizações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS update_control (
                id INTEGER PRIMARY KEY,
                last_logistics_update TIMESTAMP
            );
        """)
        
        # Tabela de logística
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logistica (
                chave_natural TEXT PRIMARY KEY,
                numero_caso TEXT,
                telefone TEXT,
                fase TEXT,
                primeiro_nome TEXT,
                placa TEXT,
                codigo TEXT,
                cep TEXT,
                email_logistica TEXT,
                codigo_novo TEXT,
                status_envio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabela com dados completos para exportação
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logistics_report (
                id INTEGER PRIMARY KEY,
                chave_natural TEXT,
                numero_caso TEXT,
                telefone TEXT,
                fase TEXT,
                primeiro_nome TEXT,
                placa TEXT,
                codigo TEXT,
                cep TEXT,
                email_logistica TEXT,
                codigo_novo TEXT,
                status_envio TEXT,
                update_timestamp TIMESTAMP
            );
        """)
        
        # Inserir registro inicial se não existir
        cursor.execute("SELECT 1 FROM update_control")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO update_control (last_logistics_update) VALUES (NULL)")
        
        conn.commit()
    print("✅ Banco de dados e tabelas configurados")

def get_google_sheet_data():
    """Coleta dados da planilha do Google Sheets"""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_KEY)
        worksheet = sheet.get_worksheet_by_id(int(SHEET_GID))
        return worksheet.get_all_records()
    except Exception as e:
        print(f"❌ Erro ao acessar planilha: {e}")
        return []

def process_sheet_data(sheet_data):
    """Processa dados da planilha e cria um dicionário de lookup por 'Chave Natural'"""
    lookup = {}
    for row in sheet_data:
        chave_natural = str(row.get('Chave Natural', '')).strip()
        if chave_natural:
            lookup[chave_natural] = {
                "numero_caso": row.get("Número do caso", ""),
                "telefone": row.get("Telefone", ""),
                "fase": row.get("Fase", ""),
                "primeiro_nome": row.get("Primeiro Nome", ""),
                "placa": row.get("Placa", ""),
                "codigo": row.get("codigo", ""),
                "cep": row.get("CEP", ""),
                "email_logistica": row.get("email", ""),
                "codigo_novo": row.get("codigo_novo", ""),
                "status_envio": row.get("status_envio", "")
            }
    return lookup

def save_logistics_data(logistica_data):
    """Salva dados de logística no banco de dados"""
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Limpar dados antigos
        cursor.execute("DELETE FROM logistica")
        cursor.execute("DELETE FROM logistics_report")
        
        # Inserir dados na tabela logistica
        for chave, dados in logistica_data.items():
            cursor.execute("""
                INSERT INTO logistica (
                    chave_natural, numero_caso, telefone, fase, 
                    primeiro_nome, placa, codigo, cep, 
                    email_logistica, codigo_novo, status_envio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                chave,
                dados["numero_caso"],
                dados["telefone"],
                dados["fase"],
                dados["primeiro_nome"],
                dados["placa"],
                dados["codigo"],
                dados["cep"],
                dados["email_logistica"],
                dados["codigo_novo"],
                dados["status_envio"]
            ))
            
            # Inserir na tabela de relatório completo
            cursor.execute("""
                INSERT INTO logistics_report (
                    chave_natural, numero_caso, telefone, fase, 
                    primeiro_nome, placa, codigo, cep, 
                    email_logistica, codigo_novo, status_envio,
                    update_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                chave,
                dados["numero_caso"],
                dados["telefone"],
                dados["fase"],
                dados["primeiro_nome"],
                dados["placa"],
                dados["codigo"],
                dados["cep"],
                dados["email_logistica"],
                dados["codigo_novo"],
                dados["status_envio"],
                update_time
            ))
        
        # Atualizar controle de atualização
        cursor.execute("UPDATE update_control SET last_logistics_update = ?", (update_time,))
        conn.commit()
    
    print(f"✅ {len(logistica_data)} registros de logística salvos")
    print(f"🕒 Última atualização: {update_time}")
    return logistica_data

def generate_report(logistica_data):
    """Gera um relatório CSV com os dados mais recentes"""
    report_path = "data/logistics_report.csv"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        # Escrever cabeçalho
        f.write("Chave Natural,Número do Caso,Telefone,Fase,Primeiro Nome,Placa,Código,CEP,Email Logística,Código Novo,Status Envio\n")
        
        # Escrever dados
        for chave, dados in logistica_data.items():
            row = [
                chave,
                dados["numero_caso"],
                dados["telefone"],
                dados["fase"],
                dados["primeiro_nome"],
                dados["placa"],
                dados["codigo"],
                dados["cep"],
                dados["email_logistica"],
                dados["codigo_novo"],
                dados["status_envio"]
            ]
            f.write(','.join(f'"{str(item)}"' for item in row) + '\n')
    
    print(f"📊 Relatório gerado em: {report_path}")

def enrich_devices_with_logistics(logistica_data):
    """Atualiza o arquivo devices_data.json com dados de logística"""
    try:
        # Carregar dados existentes dos dispositivos
        with open(DEVICES_JSON_PATH, 'r', encoding='utf-8') as f:
            devices_data = json.load(f)
        
        # Contadores para estatísticas
        total_devices = 0
        matched_devices = 0
        
        # Para cada conta no JSON
        for account, account_data in devices_data.items():
            # Para cada dispositivo na conta
            for device in account_data.get("devices", []):
                total_devices += 1
                
                # Obter o nome de configuração (chave natural)
                config_name = device.get("config", {}).get("name", "")
                
                # Verificar se existe correspondência na logística
                if config_name and config_name in logistica_data:
                    matched_devices += 1
                    # Adicionar dados de logística ao dispositivo
                    device["logistica"] = logistica_data[config_name]
        
        # Salvar o JSON enriquecido
        with open(ENRICHED_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(devices_data, f, ensure_ascii=False, indent=4)
        
        print(f"📊 Dispositivos encontrados: {total_devices}")
        print(f"📊 Dispositivos com logística: {matched_devices} ({matched_devices/total_devices*100:.1f}%)")
        print(f"✅ JSON enriquecido salvo em: {ENRICHED_JSON_PATH}")
        
    except FileNotFoundError:
        print(f"❌ Arquivo {DEVICES_JSON_PATH} não encontrado. Execute o script de coleta da API primeiro.")
    except Exception as e:
        print(f"❌ Erro ao enriquecer dados dos dispositivos: {e}")

def main():
    print("🚀 Iniciando processo de atualização de logística")
    print("-----------------------------------------------")
    
    # Configurar banco de dados
    setup_database()
    
    # Coletar dados da planilha
    print("\n⏳ Acessando Google Sheets...")
    sheet_data = get_google_sheet_data()
    
    if not sheet_data:
        print("❌ Nenhum dado coletado da planilha. Verifique as credenciais e acesso.")
        return
    
    print(f"✅ Dados coletados: {len(sheet_data)} registros")
    
    # Processar dados
    print("\n⏳ Processando dados...")
    logistica_data = process_sheet_data(sheet_data)
    print(f"✅ Dados processados: {len(logistica_data)} registros válidos")
    
    # Salvar no banco de dados
    print("\n⏳ Salvando no banco de dados...")
    save_logistics_data(logistica_data)
    
    # Gerar relatório CSV
    print("\n⏳ Gerando relatório CSV...")
    generate_report(logistica_data)
    
    # Atualizar arquivo JSON dos dispositivos com dados de logística
    print("\n⏳ Atualizando arquivo JSON dos dispositivos...")
    enrich_devices_with_logistics(logistica_data)
    
    print("\n✅ Processo de logística concluído com sucesso!")

if __name__ == "__main__":
    main()