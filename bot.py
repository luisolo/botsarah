import os
import threading
import asyncio
from flask import Flask
from telegram import Bot
from telegram.ext import Application, CommandHandler

# ===========================
# Variables de entorno
# ===========================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("⚠️ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no definidos en variables de entorno.")

TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)

# ===========================
# Inicializar Bot
# ===========================
bot = Bot(token=TELEGRAM_TOKEN)
app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()

def enviar_mensaje(texto: str):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)
    except Exception as e:
        print(f"⚠️ Error al enviar mensaje: {e}")

# ===========================
# Comandos de Telegram
# ===========================
async def status(update, context):
    await update.message.reply_text("🤖 Bot activo en Render, esperando señales...")

app_telegram.add_handler(CommandHandler("status", status))

# ===========================
# Loop principal de trading (ejemplo)
# ===========================
async def trading_loop():
    while True:
        # Aquí va tu lógica de trading, análisis y señales
        # ejemplo:
        enviar_mensaje("📈 Señal detectada: ejemplo")
        await asyncio.sleep(30*60)  # enviar cada 30 min para prueba

# ===========================
# Ejecutar Telegram en hilo
# ===========================
def run_telegram():
    asyncio.run(app_telegram.run_polling())

threading.Thread(target=run_telegram, daemon=True).start()

# ===========================
# Flask para Render
# ===========================
flask_app = Flask("BotSarah")

@flask_app.route("/")
def home():
    return "✅ Bot Sarah activo en Render"

if __name__ == "__main__":
    # Lanzar loop de trading en segundo hilo
    threading.Thread(target=lambda: asyncio.run(trading_loop()), daemon=True).start()
    # Ejecutar servidor Flask
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))