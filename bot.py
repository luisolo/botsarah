import asyncio
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from trading_strategy import ejecutar_estrategia  # tu lógica de swing

# -----------------------------
# Configuración del bot
# -----------------------------
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Estado del bot
bot_activo = False
operaciones = []  # historial de operaciones

# -----------------------------
# Funciones de Telegram
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_activo
    if not bot_activo:
        bot_activo = True
        await update.message.reply_text("✅ Bot activado")
        threading.Thread(target=main_trading_loop, daemon=True).start()
    else:
        await update.message.reply_text("⚠️ Bot ya está activo")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_activo
    bot_activo = False
    await update.message.reply_text("⛔ Bot detenido")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = "activo" if bot_activo else "detenido"
    ultima = operaciones[-1] if operaciones else "Ninguna operación aún"
    await update.message.reply_text(f"Estado del bot: {estado}\nÚltima operación: {ultima}")

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if operaciones:
        resumen_texto = "\n".join(operaciones[-10:])  # últimas 10 operaciones
    else:
        resumen_texto = "No hay operaciones aún"
    await update.message.reply_text(f"📊 Resumen reciente:\n{resumen_texto}")

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("stop", stop))
app_telegram.add_handler(CommandHandler("status", status))
app_telegram.add_handler(CommandHandler("resumen", resumen))

# -----------------------------
# Lógica de trading
# -----------------------------
def main_trading_loop():
    global bot_activo, operaciones
    while bot_activo:
        resultado = ejecutar_estrategia()  # tu función de swing
        if resultado:
            # resultado = {"par": "EURUSD", "tipo": "compra", "precio": 1.0912, "estado": "ganada"}
            operaciones.append(f"{resultado['par']} | {resultado['tipo']} | {resultado['precio']} | {resultado['estado']}")
            # Enviar notificación a Telegram
            asyncio.run_coroutine_threadsafe(
                app_telegram.bot.send_message(
                    chat_id="TU_CHAT_ID",
                    text=f"📈 Nueva operación:\n{resultado['par']} | {resultado['tipo']} | {resultado['precio']}\nResultado: {resultado['estado']}"
                ),
                app_telegram.loop
            )
        asyncio.sleep(1)  # espera breve antes de siguiente chequeo

# -----------------------------
# Servidor Flask para Render
# -----------------------------
flask_app = Flask("bot_sarah")

@flask_app.route("/")
def index():
    return "Bot Sarah activo ✅"

def run_telegram_bot():
    asyncio.run(app_telegram.run_polling(poll_interval=1.0, stop_signals=[]))

if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    flask_app.run(host="0.0.0.0", port=10000)