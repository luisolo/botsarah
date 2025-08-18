import os
import asyncio
import threading
from flask import Flask
from telegram import Bot
from telegram.ext import ApplicationBuilder

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Inicializa Flask
app = Flask("BotSarah")

@app.route("/")
def home():
    return "Bot Sarah activo y en línea"

# Inicializa Telegram
bot = Bot(token=TELEGRAM_TOKEN)
app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Función para enviar saludo al iniciar
async def saludar_inicio():
    texto = "¡Hola! El bot está en línea y listo para operar."
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

# Función principal de Telegram
async def run_telegram_async():
    await saludar_inicio()          # Envía saludo al iniciar
    await app_telegram.run_polling()  # Corre el polling de Telegram

def run_telegram():
    asyncio.run(run_telegram_async())

# Ejecuta Telegram en un hilo separado para no bloquear Flask
threading.Thread(target=run_telegram, daemon=True).start()

# ===========================================
# Aquí podrías agregar tus funciones de estrategia
# y trading, por ejemplo: trading_loop(), análisis de velas, EMA, RSI, etc.
# ===========================================

# Ejecuta Flask (Render escucha en $PORT)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)