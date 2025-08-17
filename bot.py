import os
import asyncio
import websockets
import json
from telegram import Bot
from flask import Flask
import threading

# 🔹 Variables de entorno
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DERIV_ENV = os.getenv("DERIV_ENV", "demo")

if not TELEGRAM_TOKEN:
    raise ValueError("Error: TELEGRAM_TOKEN no definido")

bot = Bot(token=TELEGRAM_TOKEN)

# 🔹 Bot principal
async def start_bot():
    url = "wss://ws.deriv.com/websockets/v6"  # URL directa, sin resolver IP manual
    while True:
        try:
            async with websockets.connect(url) as websocket:
                # Autorizar con Deriv
                await websocket.send(json.dumps({"authorize": DERIV_API_TOKEN}))
                auth_response = await websocket.recv()
                print("🔑 Autenticación exitosa:", auth_response)

                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"✅ Bot conectado a Deriv ({DERIV_ENV})"
                )

                # Ejemplo: suscribir a ticks del índice sintético R_50
                await websocket.send(json.dumps({"ticks": "R_50"}))

                while True:
                    mensaje = await websocket.recv()
                    print("📩 Mensaje recibido:", mensaje)

        except Exception as e:
            print("⚠️ Error de conexión:", e)
            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"⚠️ Error de conexión: {e}. Reintentando en 10s..."
                )
            except Exception as telegram_error:
                print(f"⚠️ Error enviando mensaje a Telegram: {telegram_error}")

            await asyncio.sleep(10)

# 🔹 Servidor HTTP mínimo para Render Web Service
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot Sarah activo ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render asigna automáticamente
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()

# 🔹 Ejecutar bot
if __name__ == "__main__":
    asyncio.run(start_bot())