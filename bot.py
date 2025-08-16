import os
import asyncio
import socket
import websockets
import json
from telegram import Bot

# 🔑 Variables de entorno
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN", "qB41nVQ9ugtd31i")  # demo token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DERIV_ENV = os.getenv("DERIV_ENV", "demo")
APP_ID = "1089"  # App ID de pruebas de Deriv

if not TELEGRAM_TOKEN:
    raise ValueError("Error: TELEGRAM_TOKEN no definido")

bot = Bot(token=TELEGRAM_TOKEN)

# 🔹 Resolver manualmente ws.deriv.com
def resolve_deriv_host():
    try:
        ip = socket.gethostbyname("ws.deriv.com")
        print(f"✅ ws.deriv.com resuelto en {ip}")
        return ip
    except Exception as e:
        print(f"⚠️ Error resolviendo ws.deriv.com: {e}")
        return None

# 🔹 Construir URI con fallback
def get_deriv_uri():
    host_ip = resolve_deriv_host()
    if host_ip:
        return f"wss://{host_ip}/websockets/v3?app_id={APP_ID}"
    else:
        return f"wss://ws.deriv.com/websockets/v3?app_id={APP_ID}"

# 🔹 Bot principal
async def start_bot():
    while True:
        uri = get_deriv_uri()
        try:
            async with websockets.connect(uri, server_hostname="ws.deriv.com") as websocket:
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

if __name__ == "__main__":
    asyncio.run(start_bot())