import requests
import threading
import time
from flask import Flask
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ====== Configuración IC Markets ======
API_TOKEN = "TU_API_TOKEN"  # Reemplaza con tu token IC Markets
BASE_URL = "https://api-demo.icmarkets.com"

# ====== Configuración Telegram ======
TELEGRAM_TOKEN = "TU_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "TU_CHAT_ID"
bot_telegram = Bot(token=TELEGRAM_TOKEN)

# ====== Variables de control ======
bot_activo = False
estado_bot = "Detenido"
operaciones = []  # Lista de dicts con info de operaciones

# ====== Capital ======
CAPITAL_INICIAL = 10000  # Ejemplo: 10,000 USD demo
capital_disponible = CAPITAL_INICIAL

# ====== Funciones IC Markets ======
def get_price(symbol="EURUSD"):
    try:
        url = f"{BASE_URL}/v1/ticks/{symbol}"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        bid = data["bid"]
        ask = data["ask"]
        return bid, ask
    except Exception as e:
        print("⚠️ Error obteniendo precio:", e)
        return None, None

# ====== Estrategia Swing Trading ======
def analizar_estrategia(symbol="EURUSD"):
    bid, ask = get_price(symbol)
    if bid is None:
        return None

    # Placeholder: lógica de 6 condiciones
    tendencia = True
    soporte_resistencia = True
    patron_vela = True
    ema20 = True
    rsi = False
    volumen = True

    condiciones_cumplidas = sum([tendencia, soporte_resistencia, patron_vela, ema20, rsi, volumen])

    if condiciones_cumplidas >= 4:
        tipo = "BUY" if bid % 2 == 0 else "SELL"  # placeholder decisión
        return tipo, bid
    return None

# ====== Ejecutar operación ======
def ejecutar_operacion(symbol="EURUSD"):
    global capital_disponible

    resultado_estrategia = analizar_estrategia(symbol)
    if not resultado_estrategia:
        return

    tipo, precio_entrada = resultado_estrategia

    # Calcular tamaño de la posición (1% del capital disponible)
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

    bot_telegram.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"💹 Operación ABIERTA: {symbol} | {tipo} | Entrada: {precio_entrada} | Monto: {monto_operacion:.2f}"
    )
    print(f"Operación ABIERTA: {symbol} | {tipo} | Entrada: {precio_entrada} | Monto: {monto_operacion:.2f}")

    # Simular cierre de operación después de 10 segundos (placeholder)
    time.sleep(10)
    cierre = precio_entrada * 1.001 if tipo == "BUY" else precio_entrada * 0.999
    resultado = "GANADA" if (tipo == "BUY" and cierre > precio_entrada) or (tipo == "SELL" and cierre < precio_entrada) else "PERDIDA"

    # Ajustar capital según resultado
    if resultado == "GANADA":
        ganancia = monto_operacion * 0.001  # placeholder PnL
        capital_disponible += ganancia
    else:
        perdida = monto_operacion * 0.001
        capital_disponible -= perdida

    operacion["estado"] = "CERRADA"
    operacion["cierre"] = cierre
    operacion["resultado"] = resultado

    bot_telegram.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"📌 Operación CERRADA: {symbol} | {tipo} | Resultado: {resultado} | Cierre: {cierre} | Capital disponible: {capital_disponible:.2f}"
    )
    print(f"Operación CERRADA: {symbol} | {tipo} | Resultado: {resultado} | Cierre: {cierre} | Capital disponible: {capital_disponible:.2f}")

# ====== Loop de estrategia ======
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
def start(update: Update, context: CallbackContext):
    global bot_activo
    bot_activo = True
    update.message.reply_text("✅ Bot ACTIVADO. Comenzará a ejecutar operaciones.")

def stop(update: Update, context: CallbackContext):
    global bot_activo
    bot_activo = False
    update.message.reply_text("🛑 Bot DETENIDO. No ejecutará nuevas operaciones.")

def status(update: Update, context: CallbackContext):
    update.message.reply_text(f"📊 Estado del bot: {estado_bot}\nCapital disponible: {capital_disponible:.2f}\nOperaciones realizadas: {len(operaciones)}")

def resumen(update: Update, context: CallbackContext):
    if not operaciones:
        update.message.reply_text("📋 No se han realizado operaciones aún.")
        return
    msg = "📋 Resumen de operaciones:\n"
    for op in operaciones:
        if op["estado"] == "CERRADA":
            msg += f"{op['symbol']} | {op['tipo']} | Entrada: {op['entrada']} | Cierre: {op['cierre']} | Resultado: {op['resultado']} | Monto: {op['monto']:.2f}\n"
        else:
            msg += f"{op['symbol']} | {op['tipo']} | Entrada: {op['entrada']} | Estado: {op['estado']} | Monto: {op['monto']:.2f}\n"
    update.message.reply_text(msg)

# ====== Inicializar Telegram Bot ======
def start_telegram_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("resumen", resumen))
    updater.start_polling()
    print("✅ Telegram Bot iniciado")
    updater.idle()

# ====== Servidor Flask ======
app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Bot Sarah IC Markets corriendo en Render con estrategia de swing y gestión de capital 1% por operación"

# ====== Main ======
if __name__ == "__main__":
    threading.Thread(target=run_strategy, daemon=True).start()
    threading.Thread(target=start_telegram_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)