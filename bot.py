import MetaTrader5 as mt5
from flask import Flask
import time

# ====== Configuración MT5 ======
ACCOUNT = 12345678          # <- tu número de cuenta ICMarkets
PASSWORD = "TU_PASSWORD"    # <- tu contraseña
SERVER = "ICMarketsSC-Demo" # <- servidor ICMarkets (Demo o Real)

# Inicializar MT5
def connect_mt5():
    if not mt5.initialize(login=ACCOUNT, password=PASSWORD, server=SERVER):
        print("❌ Error al conectar a MT5:", mt5.last_error())
        return False
    print("✅ Conectado a MT5 con éxito")
    return True

# Estrategia simple (ejemplo placeholder)
def run_strategy():
    print("🔎 Ejecutando estrategia Sarah...")
    # Aquí luego pondremos tu lógica de swing trading
    time.sleep(10)  # simula análisis cada 10s

# ====== Flask Server ======
app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Bot Sarah MT5 está corriendo en Render"

# ====== Main Loop ======
if __name__ == "__main__":
    if connect_mt5():
        print("📡 Bot iniciado correctamente")
        # Ejecutar en un loop paralelo al servidor
        import threading
        threading.Thread(target=lambda: [run_strategy() for _ in iter(int, 1)], daemon=True).start()
        # Levantar servidor web para Render
        app.run(host="0.0.0.0", port=10000)