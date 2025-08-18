import os
import threading
import time
from flask import Flask
import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio

# --- VARIABLES DE ENTORNO ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or "TU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "TU_CHAT_ID_AQUI"

# --- BOT TELEGRAM ---
bot = Bot(token=TELEGRAM_TOKEN)
app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()

# Saludo automático al iniciar
bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🤖 Bot Sarah en línea y listo!")

# Comando opcional /start
def start(update, context):
    update.message.reply_text("Hola! Bot Sarah activo ✅")

app_telegram.add_handler(CommandHandler("start", start))

# --- FUNCIONES DE ESTRATEGIA SARAH ---
def analizar_mercado():
    """
    Aquí se implementa tu lógica de análisis:
    - estructura de tendencia
    - soporte/resistencia
    - patrones de velas
    - EMA20
    - RSI
    - volumen
    Retorna un diccionario con señales detectadas.
    """
    # Placeholder de ejemplo
    señales = [
        {"par": "EURUSD", "tipo": "alcista", "confirmada": True},
        {"par": "USDJPY", "tipo": "bajista", "confirmada": False},
    ]
    return señales

def enviar_senal_telegram(senal):
    texto = f"📈 Señal detectada: {senal['par']} - {senal['tipo'].upper()}"
    if senal.get("confirmada"):
        texto += " ✅ Confirmada"
    else:
        texto += " ❌ Descartada"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

# --- HILO DE MONITOREO DE SEÑALES ---
def hilo_senales():
    while True:
        try:
            señales = analizar_mercado()
            for senal in señales:
                enviar_senal_telegram(senal)
            time.sleep(30*60)  # cada 30 minutos
        except Exception as e:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ Error en análisis: {e}")
            time.sleep(60)

# --- INICIAR HILO DE SEÑALES ---
thread_senales = threading.Thread(target=hilo_senales, daemon=True)
thread_senales.start()

# --- FLASK PARA MANTENER RENDER ACTIVO ---
app = Flask("BotSarah")

@app.route("/")
def home():
    return "Bot Sarah activo ✅"

# --- EJECUTAR BOT TELEGRAM EN EL HILO PRINCIPAL ---
if __name__ == "__main__":
    # Iniciar Flask en otro hilo para que no bloquee Telegram
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    # Ejecutar Telegram polling en el hilo principal
    app_telegram.run_polling()