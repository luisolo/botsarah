import asyncio
import time
from threading import Thread
from flask import Flask
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== Configuración IC Markets ======
API_TOKEN = "TU_API_TOKEN"  # Reemplaza con tu token IC Markets
BASE_URL = "https://api-demo.icmarkets.com"

# ====== Configuración Telegram ======
TELEGRAM_TOKEN = "TU_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "TU_CHAT_ID"

# ====== Variables de control ======
bot_activo = False
estado_bot = "Detenido"
operaciones = []  # Lista de dicts con info de operaciones
CAPITAL_INICIAL = 10000
capital_disponible = CAPITAL_INICIAL

# ====== Funciones placeholder IC Markets ======
def get_price(symbol="EURUSD"):
    # Aquí va tu request real a IC Markets API
    # Placeholder: devuelve un precio simulado
    bid = 1.1000
    ask = 1.1002
    return bid, ask

def analizar_estrategia(symbol="EURUSD"):
    bid, ask = get_price(symbol)
    if bid is None:
        return None

    # Placeholder: lógica de 6 condiciones
    condiciones = [True, True, True, True, False, True]
    if sum(condiciones) >= 4:
        tipo = "BUY" if bid % 2 == 0 else "SELL"
        return tipo, bid
    return None

def ejecutar_operacion(symbol="EURUSD"):
    global capital_disponible
    resultado_estrategia = analizar_estrategia(symbol)
    if not resultado_estrategia:
        return

    tipo, precio_entrada = resultado_estrategia
    monto_operacion = capital_disponible * 0.01

    operacion = {
        "symbol": symbol,
        "tipo": tipo,
        "entrada": precio_entrada,
        "monto": monto_operacion,
        "estado": "ABIERTA",
        "resultado": None
    }
    operaciones.append(operacion)

    # Notificar apertura
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"💹 Operación ABIERTA: {symbol} | {tipo} | Entrada: {precio_entrada} | Monto: {monto_operacion:.2f}"
    )
    print(f"Operación ABIERTA: {symbol} | {tipo} | Entrada: {precio_entrada} | Monto: {monto_operacion:.2f}")

    # Simular cierre
    time.sleep(10)
    cierre = precio_entrada * 1.001 if tipo == "BUY" else precio_entrada * 0.999
    resultado = "GANADA" if (tipo == "BUY" and cierre > precio_entrada) or (tipo == "SELL" and cierre < precio_entrada) else "PERDIDA"

    if resultado == "GANADA":
        capital_disponible += monto_operacion * 0.001
    else:
        capital_disponible -= monto_operacion * 0.001

    operacion["estado"] = "CERRADA"
    operacion["cierre"] = cierre
    operacion["resultado"] = resultado

    # Notificar cierre
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"📌 Operación CERRADA: {symbol} | {tipo} | Resultado: {resultado} | Cierre: {cierre:.5f} | Capital disponible: {capital_disponible:.2f}"
    )
    print(f"Operación CERRADA: {symbol} | {tipo} | Resultado: {resultado} | Cierre: {cierre:.5f} | Capital disponible: {capital_disponible:.2f}")

# ====== Loop estrategia ======
def run_strategy():
    global estado_bot
    while True:
        if bot_activo:
            estado_bot = "Analizando mercado y ejecutando estrategia"
            ejecutar_operacion("EURUSD")
        else:
            estado_bot = "Detenido"
        time.sleep(5)

# ====== Comandos Telegram ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_activo
    bot_activo = True
    await update.message.reply_text("✅ Bot ACTIVADO. Comenzará a ejecutar operaciones.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_activo
    bot_activo = False
    await update.message.reply_text("🛑 Bot DETENIDO. No ejecutará nuevas operaciones.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 Estado del bot: {estado_bot}\nCapital disponible: {capital_disponible:.2f}\nOperaciones realizadas: {len(operaciones)}"
    )

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not operaciones:
        await update.message.reply_text("📋 No se han realizado operaciones aún.")
        return
    msg = "📋 Resumen de operaciones:\n"
    for op in operaciones:
        if op["estado"] == "CERRADA":
            msg += f"{op['symbol']} | {op['tipo']} | Entrada: {op['entrada']} | Cierre: {op['cierre']} | Resultado: {op['resultado']} | Monto: {op['monto']:.2f}\n"
        else:
            msg += f"{op['symbol']} | {op['tipo']} | Entrada: {op['entrada']} | Estado: {op['estado']} | Monto: {op['monto']:.2f}\n"
    await update.message.reply_text(msg)

async def main_telegram():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("resumen", resumen))
    print("✅ Telegram Bot iniciado")
    await app.run_polling()

# ====== Flask ======
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "🚀 Bot Sarah IC Markets corriendo en Render con estrategia swing y gestión 1% capital"

# ====== Main ======
if __name__ == "__main__":
    # Ejecutar estrategia en hilo separado
    Thread(target=run_strategy, daemon=True).start()
    # Ejecutar Telegram en hilo principal con asyncio
    asyncio.run(main_telegram())
    # Flask opcional si quieres exponer web endpoint
    # flask_app.run(host="0.0.0.0", port=10000, threaded=True)