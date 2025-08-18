import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------------- Flask para mantener vivo el servicio ----------------
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot Sarah activo en Render"

# ---------------- Telegram Bot ----------------
TOKEN = "TU_TOKEN_TELEGRAM"  # reemplaza con tu token
app_telegram = ApplicationBuilder().token(TOKEN).build()

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Sarah activo ✅")

app_telegram.add_handler(CommandHandler("status", status))

# ---------------- Trading (integrar tu lógica aquí) ----------------
def trading_loop():
    import time
    while True:
        try:
            # ---------------- Ejemplo de lógica ----------------
            # Aquí agregas tu análisis técnico de Sarah (EMA, RSI, velas, volumen, etc.)
            par = "EURUSD"
            tipo_entrada = "ALCISTA"
            resultado = "GANADA"  # o "PERDIDA"
            mensaje = f"Señal: {par} {tipo_entrada}\nResultado: {resultado}"
            
            # Enviar mensaje a Telegram
            asyncio.run_coroutine_threadsafe(
                app_telegram.bot.send_message(chat_id=TU_CHAT_ID, text=mensaje),
                app_telegram.loop
            )

            time.sleep(1800)  # Espera 30 minutos entre señales de ejemplo
        except Exception as e:
            print("Error en trading_loop:", e)
            time.sleep(5)

# ---------------- Hilos ----------------
threading.Thread(target=lambda: asyncio.run(app_telegram.run_polling()), daemon=True).start()
threading.Thread(target=trading_loop, daemon=True).start()

# ---------------- Ejecutar Flask ----------------
if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=10000)