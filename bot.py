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

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Error: TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no definidos.")

bot = Bot(token=TELEGRAM_TOKEN)

async def conectar_deriv():
    url = "wss://ws.binaryws.com/websockets/v6"
    while True:
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps({"authorize": DERIV_API_TOKEN}))
                auth_response = await websocket.recv()
                print("Autenticación exitosa:", auth_response)

                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"Bot conectado a Deriv ({DERIV_ENV}) ✅"
                )

                while True:
                    mensaje = await websocket.recv()
                    print("Mensaje recibido:", mensaje)

        except Exception as e:
            print("Error de conexión:", e)
            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"Error de conexión: {e}. Reintentando en 10s..."
                )
            except Exception as e2:
                print("Error al notificar en Telegram:", e2)
            await asyncio.sleep(10)

def main():
    asyncio.run(conectar_deriv())