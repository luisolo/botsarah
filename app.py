import os
import threading
import asyncio
from flask import Flask
from bot import start_bot

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 8000))

@app.route("/")
def index():
    return "Bot de Deriv activo ✅"

def run_bot():
    asyncio.run(start_bot())

if __name__ == "__main__":
    # Ejecutar el bot en un hilo aparte para que Flask siga corriendo
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=PORT)