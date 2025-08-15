import os
import asyncio
import websockets
import json
from telegram import Bot

# Variables de entorno
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DERIV_ENV = os.getenv("DERIV_ENV", "demo")

if not TELEGRAM_TOKEN:
    raise ValueError("Error: TELEGRAM_TOKEN no definido")

bot = Bot(token=TELEGRAM_TOKEN)

async def start_bot():
    url = "wss://ws.binaryws.com/websockets/v6"
    while True:
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps({"authorize": DERIV_API_TOKEN}))
                auth_response = await websocket.recv()
                print("Autenticación exitosa:", auth_response)

                await bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                       text=f"Bot conectado a Deriv ({DERIV_ENV}) ✅")

                while True:
                    mensaje = await websocket.recv()
                    print("Mensaje recibido:", mensaje)

        except Exception as e:
            print("Error de conexión:", e)
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                   text=f"Error de conexión: {e}. Reintentando en 10s...")
            await asyncio.sleep(10)