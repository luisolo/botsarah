import os
import threading
import time
import random
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

# -----------------------------
# Variables de entorno
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ICMARKETS_API_KEY = os.getenv("ICMARKETS_API_KEY")  # ejemplo si usas API
BOT_RUNNING = False
CAPITAL = 10000  # ejemplo inicial
POSICION_ACTUAL = None

# -----------------------------
# Estrategia swing (ejemplo)
# -----------------------------
def estrategia_swing():
    """
    Simula decisión de trading.
    Reemplaza con tus reglas reales de swing trading
    """
    decision = random.choice(["BUY", "SELL", None])  # None = no operar
    return decision

# -----------------------------
# Funciones Telegram
# -----------------------------
def start(update, context):
    global BOT_RUNNING
    BOT_RUNNING = True
    context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Bot activado. Estrategia swing en ejecución...")

def stop(update, context):
    global BOT_RUNNING
    BOT_RUNNING = False
    context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🛑 Bot detenido.")

def status(update, context):
    estado = "activo" if BOT_RUNNING else "detenido"
    msg = f"Bot está actualmente: {estado}\nPosición actual: {POSICION_ACTUAL}\nCapital: ${CAPITAL:.2f}"
    context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def resumen(update, context):
    msg = f"Resumen rápido:\nCapital actual: ${CAPITAL:.2f}\nPosición actual: {POSICION_ACTUAL}"
    context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# -----------------------------
# Función principal de trading
# -----------------------------
def trading_loop():
    global CAPITAL, POSICION_ACTUAL, BOT_RUNNING
    while True:
        if BOT_RUNNING:
            decision = estrategia_swing()
            if decision:
                monto_operacion = CAPITAL * 0.01  # 1% del capital
                POSICION_ACTUAL = f"{decision} ${monto_operacion:.2f}"
                # Simula resultado
                resultado = random.choice(["GANADA", "PERDIDA"])
                if resultado == "GANADA":
                    CAPITAL += monto_operacion * 0.8  # ejemplo ganancia 80%
                else:
                    CAPITAL -= monto_operacion
                # Notificar en Telegram
                try:
                    app_telegram.bot.send_message(
                        chat_id=TELEGRAM_CHAT_ID,
                        text=f"💹 {POSICION_ACTUAL}\nResultado: {resultado}\nCapital actualizado: ${CAPITAL:.2f}"
                    )
                except Exception as e:
                    print(f"⚠️ Error enviando mensaje Telegram: {e}")
                POSICION_ACTUAL = None
        time.sleep(60)  # espera 1 minuto entre evaluaciones

# -----------------------------
# Flask app (para Render)
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Sarah corriendo en Render 🚀"

# -----------------------------
# Inicializar Telegram en hilo
# -----------------------------
app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("stop", stop))
app_telegram.add_handler(CommandHandler("status", status))
app_telegram.add_handler(CommandHandler("resumen", resumen))

threading.Thread(target=lambda: app_telegram.run_polling(poll_interval=1.0, stop_signals=[]), daemon=True).start()

# -----------------------------
# Inicializar loop de trading en hilo
# -----------------------------
threading.Thread(target=trading_loop, daemon=True).start()

# -----------------------------
# Ejecutar Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))