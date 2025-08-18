import requests
from flask import Flask
import threading
import time

# ====== Configuración IC Markets ======
API_TOKEN = "TU_API_TOKEN"  # Reemplaza con tu token IC Markets
BASE_URL = "https://api-demo.icmarkets.com"  # Demo, cambia a real si es necesario

# ====== Funciones del bot ======
def get_price(symbol="EURUSD"):
    try:
        url = f"{BASE_URL}/v1/ticks/{symbol}"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        bid = data["bid"]
        ask = data["ask"]
        print(f"💹 {symbol} - Bid: {bid} | Ask: {ask}")
        return bid, ask
    except Exception as e:
        print("⚠️ Error obteniendo precio:", e)
        return None, None

def run_strategy():
    while True:
        print("🔎 Ejecutando estrategia Sarah en IC Markets...")
        get_price("EURUSD")
        time.sleep(10)  # analizar cada 10 segundos

# ====== Servidor Flask ======
app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Bot Sarah IC Markets corriendo en Render"

# ====== Main ======
if __name__ == "__main__":
    print("📡 Bot iniciado correctamente")
    # Ejecutar estrategia en hilo paralelo
    threading.Thread(target=run_strategy, daemon=True).start()
    # Levantar servidor web para Render
    app.run(host="0.0.0.0", port=10000)