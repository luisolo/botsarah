from flask import Flask
import asyncio
import threading
from bot import conectar_deriv  # Importamos la función de bot.py

app = Flask(__name__)

# Endpoint de salud para Render
@app.route("/health")
def health():
    return "Bot activo ✅", 200

# Función para correr asyncio en un hilo separado
def start_bot():
    asyncio.run(conectar_deriv())

# Iniciamos el bot en segundo plano
threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)