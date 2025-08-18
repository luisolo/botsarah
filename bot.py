import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI"

# --- HANDLER COMANDO /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Bot Sarah activo ✅")

# --- TELEGRAM BOT ---
async def telegram_bot():
    # Crear la aplicación de Telegram
    app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Agregar handler /start
    app_telegram.add_handler(CommandHandler("start", start))
    
    # Saludo automático al iniciar
    bot = Bot(TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🤖 Bot Sarah en línea y listo!")

    # Iniciar polling
    await app_telegram.run_polling()

# --- MAIN ---
if __name__ == "__main__":
    asyncio.run(telegram_bot())