from flask import Flask
import os
import threading
import bot  # Importa tu bot.py

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot Sarah activo en Render ✅"

# Ejecutar bot en un hilo separado para que Flask siga corriendo
def run_bot():
    import asyncio
    asyncio.run(bot.conectar_deriv())

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render asigna la variable PORT
    app.run(host="0.0.0.0", port=port)