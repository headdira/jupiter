import requests
import json
import os
import sqlite3
from hashlib import md5
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração (mantém igual)
API_AUTH_URL = "http://openapi.tftiot.com/v2/auth/action"
API_DEVICES_URL = "https://openapi.tftiot.com/v2/devices"
API_LBS_URL = "https://openapi.tftiot.com/v2/devices/action"
EMAILS = [
    "loovirj@loovi.com.br",
    "loovirj2@loovi.com.br",
    "loovimg@loovi.com.br",
    "loovidf@loovi.com.br",
    "loovice@loovi.com.br",
    "loovies@loovi.com.br",
    "loovirs@loovi.com.br",
    "loovigo@loovi.com.br",
    "looviac@loovi.com.br",
    "loovipe@loovi.com.br",
    "loovisp1@loovi.com.br",
    "loovisp2@loovi.com.br",
    "loovisp3@loovi.com.br",
    "loovisp4@loovi.com.br",
    "loovisp5@loovi.com.br",
    "loovisp6@loovi.com.br",
    "loovisp7@loovi.com.br",
    "loovisp8@loovi.com.br",
    "loovisp9@loovi.com.br",
    "loovisp10@loovi.com.br",
    "loovial@loovi.com.br",
    "looviam@loovi.com.br",
    "looviap@loovi.com.br",
    "looviba@loovi.com.br",
    "loovice@loovi.com.br",
    "loovidf@loovi.com.br",
    "loovima@loovi.com.br",
    "loovims@loovi.com.br",
    "loovimt@loovi.com.br",
    "loovipa@loovi.com.br",
    "loovipb@loovi.com.br",
    "loovipe@loovi.com.br",
    "loovipi@loovi.com.br",
    "loovipr@loovi.com.br",
    "loovirj2@loovi.com.br",
    "loovirn@loovi.com.br",
    "looviro@loovi.com.br",
    "loovirr@loovi.com.br",
    "loovisc@loovi.com.br",
    "loovise@loovi.com.br",
    "loovito@loovi.com.br"
]
PASSWORD = "123456"
DB_PATH = "data/devices_data.sqlite"
JSON_PATH = "data/devices_data.json"

def gerar_token(email):
    payload = {
        "getAccessToken": {
            "account": email,
            "password-md5": md5(PASSWORD.encode()).hexdigest(),
            "client-type": "web",
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_AUTH_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        token = data.get("access-token")
        if token:
            print(f"✅ Token gerado para {email}")
            return token
        else:
            print(f"❌ Token não encontrado para {email}: {data}")
            return None
    except Exception as e:
        print(f"❌ Erro ao gerar token para {email}:", e)
        return None

def buscar_dispositivos(token):
    try:
        response = requests.get(f"{API_DEVICES_URL}?access-token={token}", timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao buscar dispositivos:", e)
        return None

def buscar_lbs(token, imei):
    payload = {"getLbsLatLng": {"imei": imei}}
    headers = {"Content-Type": "application/json"}
    params = {"access-token": token}
    try:
        response = requests.post(API_LBS_URL, json=payload, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0:
            return imei, data.get("lat"), data.get("lng")
        else:
            print(f"❌ Erro LBS para IMEI {imei}: {data}")
            return imei, None, None
    except Exception as e:
        print(f"❌ Erro ao buscar LBS para IMEI {imei}:", e)
        return imei, None, None

def simplificar_dados(email, dados, token):
    dispositivos = dados.get("devices", [])
    simplificados = []

    # Coletar todos os IMEIs para buscar LBS em paralelo
    imeis = [d.get("imei") for d in dispositivos if d.get("imei")]

    # Usar ThreadPoolExecutor para buscar LBS de forma concorrente
    lbs_results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(buscar_lbs, token, imei): imei for imei in imeis}
        for future in as_completed(futures):
            imei, lat, lng = future.result()
            lbs_results[imei] = (lat, lng)

    for dispositivo in dispositivos:
        imei = dispositivo.get("imei")
        lbs_lat, lbs_lng = lbs_results.get(imei, (None, None))

        simplificado = {
            "model": dispositivo.get("model"),
            "imei": imei,
            "status": {
                "address": dispositivo.get("status", {}).get("address", ""),
                "date": dispositivo.get("status", {}).get("date"),
                "heartbeat_time": dispositivo.get("status", {}).get("heartbeat_time"),
                "lat": dispositivo.get("status", {}).get("lat"),
                "latlng_valid": dispositivo.get("status", {}).get("latlng_valid"),
                "lng": dispositivo.get("status", {}).get("lng"),
                "location_date": dispositivo.get("status", {}).get("location_date"),
                "network_signal": dispositivo.get("status", {}).get("network_signal"),
            },
            "config": {
                "name": dispositivo.get("config", {}).get("name"),
            },
            "device_key": dispositivo.get("device_key"),
            "lbs_position": {
                "lat": lbs_lat,
                "lng": lbs_lng
            }
        }
        simplificados.append(simplificado)

    return {email: {"code": dados.get("code", 0), "devices": simplificados}}

def criar_tabela():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices_data (
                email TEXT NOT NULL,
                model TEXT,
                imei TEXT,
                address TEXT,
                date INTEGER,
                heartbeat_time TEXT,
                lat REAL,
                latlng_valid INTEGER,
                lng REAL,
                location_date INTEGER,
                network_signal INTEGER,
                config_name TEXT,
                device_key TEXT,
                lbs_lat REAL,
                lbs_lng REAL
            );
        """)
        conn.commit()
    print("✅ Tabela criada ou já existe no banco de dados")

def inserir_dados(email, dispositivos):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for dispositivo in dispositivos:
            cursor.execute("""
                INSERT INTO devices_data (
                    email, model, imei, address, date, heartbeat_time, 
                    lat, latlng_valid, lng, location_date, network_signal, 
                    config_name, device_key, lbs_lat, lbs_lng
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                email,
                dispositivo.get("model"),
                dispositivo.get("imei"),
                dispositivo.get("status", {}).get("address"),
                dispositivo.get("status", {}).get("date"),
                dispositivo.get("status", {}).get("heartbeat_time"),
                dispositivo.get("status", {}).get("lat"),
                dispositivo.get("status", {}).get("latlng_valid"),
                dispositivo.get("status", {}).get("lng"),
                dispositivo.get("status", {}).get("location_date"),
                dispositivo.get("status", {}).get("network_signal"),
                dispositivo.get("config", {}).get("name"),
                dispositivo.get("device_key"),
                dispositivo.get("lbs_position", {}).get("lat"),
                dispositivo.get("lbs_position", {}).get("lng"),
            ))
        conn.commit()
    print(f"✅ Dados inseridos no banco para o e-mail {email}")

def main():
    os.makedirs("data", exist_ok=True)
    criar_tabela()
    all_data = {}

    for email in EMAILS:
        token = gerar_token(email)
        if token:
            dispositivos = buscar_dispositivos(token)
            if dispositivos:
                simplificados = simplificar_dados(email, dispositivos, token)
                all_data.update(simplificados)
                inserir_dados(email, simplificados[email]["devices"])

    with open(JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)
    print(f"✅ Dados simplificados e com LBS salvos em: {JSON_PATH}")

if __name__ == "__main__":
    main()
