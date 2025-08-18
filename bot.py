import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ----------------------------
# Configuración
# ----------------------------
TELEGRAM_TOKEN = "TU_TELEGRAM_TOKEN"
app_web = Flask(__name__)

# Estado del bot
bot_activo = False

# ----------------------------
# Comandos de Telegram
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_activo
    bot_activo = True
    await update.message.reply_text("✅ Bot iniciado")
    # Aquí podrías iniciar tu estrategia Swing async
    # asyncio.create_task(estrategia_swing(context))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_activo
    bot_activo = False
    await update.message.reply_text("🛑 Bot detenido")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = "activo" if bot_activo else "detenido"
    await update.message.reply_text(f"⚡ Estado del bot: {estado}")

# ----------------------------
# Inicializar Telegram
# ----------------------------
async def iniciar_telegram():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("status", status))

    print("✅ Telegram Bot iniciado")
    await application.run_polling()

# ----------------------------
# Flask - Endpoint web simple
# ----------------------------
@app_web.route("/")
def home():
    return "Bot Sarah activo en Render!"

# ----------------------------
# Ejecutar Flask y Telegram juntos
# ----------------------------
async def main():
    # Lanzar Flask en una tarea async separada
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(app_web.run, host="0.0.0.0", port=10000, debug=False))

    # Iniciar Telegram
    await iniciar_telegram()

# ----------------------------
# Ejecutar todo
# ----------------------------
if __name__ == "__main__":
    asyncio.run(main())