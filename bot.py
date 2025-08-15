import os
import asyncio
import websockets
import json
from telegram import Bot
from flask import Flask

# Inicializar Flask para que Render reconozca un servicio web
app = Flask(__name__)

# Cargar variables de entorno
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DERIV_ENV = os.getenv("DERIV_ENV", "demo")
PORT = int(os.getenv("PORT", 8000))  # Render asigna el puerto automáticamente

# Verificación del token
if not TELEGRAM_TOKEN:
    raise ValueError("Error: La variable de entorno TELEGRAM_TOKEN no está definida o es incorrecta.")

bot = Bot(token=TELEGRAM_TOKEN)

async def conectar_deriv():
    url = "wss://ws.binaryws.com/websockets/v6"

    while True:
        try:
            async with websockets.connect(url) as websocket:
                # Autenticación
                await websocket.send(json.dumps({"authorize": DERIV_API_TOKEN}))
                auth_response = await websocket.recv()
                print("Autenticación exitosa:", auth_response)

                await bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                       text=f"Bot conectado a Deriv ({DERIV_ENV}) ✅")

                # Loop de recepción de mensajes
                while True:
                    mensaje = await websocket.recv()
                    print("Mensaje recibido:", mensaje)

        except Exception as e:
            print("Error de conexión:", e)
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                   text=f"Error de conexión: {e}. Reintentando en 10s...")
            await asyncio.sleep(10)  # Reintento automático

# Ruta de prueba para Render
@app.route("/")
def home():
    return "Bot activo en Render ✅"

def main():
    # Ejecutar la conexión a Deriv en segundo plano
    asyncio.create_task(conectar_deriv())

    # Ejecutar Flask como servicio web
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(conectar_deriv())