import asyncio
import os
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Bot Sarah activo ✅")

async def main():
    # Crear aplicación del bot
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registrar comando /start
    app.add_handler(CommandHandler("start", start_command))

    # Enviar mensaje de saludo automático al iniciar
    bot = app.bot
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🤖 Bot Sarah en línea y listo!")

    # Iniciar el bot
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()  # Mantener el bot corriendo

if __name__ == "__main__":
    asyncio.run(main())