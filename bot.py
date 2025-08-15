import os
import asyncio
import websockets
import json
from telegram import Bot
from flask import Flask
import threading

# =====================
# Variables de entorno
# =====================
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DERIV_ENV = os.getenv("DERIV_ENV", "demo")

# Verificación del token
if not TELEGRAM_TOKEN:
    raise ValueError("Error: La variable de entorno TELEGRAM_TOKEN no está definida o es incorrecta.")

bot = Bot(token=TELEGRAM_TOKEN)

# =====================
# Función principal del bot
# =====================
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

                # Loop de recepción de mensajes (placeholder para estrategia Sarah)
                while True:
                    mensaje = await websocket.recv()
                    print("Mensaje recibido:", mensaje)

        except Exception as e:
            print("Error de conexión:", e)
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                   text=f"Error de conexión: {e}. Reintentando en 10s...")
            await asyncio.sleep(10)  # Reintento automático

# =====================
# Función para correr el bot en hilo separado
# =====================
def iniciar_bot():
    asyncio.run(conectar_deriv())

# =====================
# Configuración de Flask para servicio web
# =====================
app = Flask(__name__)

@app.route("/health")
def health():
    return "Bot activo ✅", 200

# =====================
# Inicio del bot en segundo plano + servidor web
# =====================
if __name__ == "__main__":
    # Ejecutar el bot en un hilo separado para que Flask pueda correr
    threading.Thread(target=iniciar_bot).start()
    # Ejecutar Flask en el puerto 8000 (Render detecta el servicio web)
    app.run(host="0.0.0.0", port=8000)