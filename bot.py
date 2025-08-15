import os
import asyncio
import websockets
import json
from telegram import Bot

# Cargar variables de entorno
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DERIV_ENV = os.getenv("DERIV_ENV", "demo")

# Verificación del token de Telegram
if not TELEGRAM_TOKEN:
    raise ValueError("Error: La variable de entorno TELEGRAM_TOKEN no está definida o es incorrecta.")

bot = Bot(token=TELEGRAM_TOKEN)

async def conectar_deriv():
    url = "wss://ws.binaryws.com/websockets/v6"

    while True:
        try:
            async with websockets.connect(url) as websocket:
                # Enviar token en formato correcto
                auth_payload = {
                    "authorize": DERIV_API_TOKEN
                }
                await websocket.send(json.dumps(auth_payload))

                auth_response = await websocket.recv()
                auth_data = json.loads(auth_response)

                if "error" in auth_data:
                    raise Exception(f"Autenticación fallida: {auth_data['error']['message']}")

                print("Autenticación exitosa:", auth_data)
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

def main():
    print("Bot inicializado en Render")
    asyncio.run(conectar_deriv())

if __name__ == "__main__":
    main()