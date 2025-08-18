# bot.py
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Chat donde se enviará el saludo de inicio

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Sarah activo y listo!")

# Mensaje de saludo al iniciar (opcional)
async def send_startup_message(app):
    if TELEGRAM_CHAT_ID:
        try:
            await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🤖 Bot Sarah en línea y listo!")
        except Exception as e:
            print(f"Error al enviar mensaje de inicio: {e}")

def main():
    # Crear la aplicación del bot
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Agregar manejadores de comandos
    app.add_handler(CommandHandler("start", start))

    # Enviar mensaje de inicio después de inicializar el bot
    app.post_init(send_startup_message)

    # Ejecutar el bot
    app.run_polling()

if __name__ == "__main__":
    main()