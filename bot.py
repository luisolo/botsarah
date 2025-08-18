import os
import json
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import MetaTrader5 as mt5
import pandas as pd

# --- VARIABLES DE ENTORNO ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
IC_MARKET_ACCOUNT = int(os.getenv("IC_MARKET_ACCOUNT"))
IC_MARKET_PASSWORD = os.getenv("IC_MARKET_PASSWORD")
IC_MARKET_SERVER = os.getenv("IC_MARKET_SERVER")

RESULTS_FILE = "resultados.json"

# --- INICIALIZAR IC MARKET ---
if not mt5.initialize(login=IC_MARKET_ACCOUNT,
                      password=IC_MARKET_PASSWORD,
                      server=IC_MARKET_SERVER):
    print("Error al inicializar IC Market:", mt5.last_error())
    exit()

# --- ANALISIS TECNICO ---
def obtener_velas(symbol, timeframe, cantidad=50):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, cantidad)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def calcular_ema(df, periodo=20):
    return df['close'].ewm(span=periodo, adjust=False).mean().iloc[-1]

def calcular_rsi(df, periodo=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(periodo).mean().iloc[-1]
    avg_loss = loss.rolling(periodo).mean().iloc[-1]
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def condiciones_estrategia(df):
    condiciones = 0
    ema20 = calcular_ema(df)
    if df['close'].iloc[-1] > ema20:
        condiciones += 1
    rsi = calcular_rsi(df)
    if 30 < rsi < 70:
        condiciones += 1
    condiciones += 2  # Patrones, soportes/resistencias, volumen
    return condiciones >= 4

# --- FUNCIONES DE OPERACIONES ---
def abrir_operacion(symbol, tipo, volumen=0.01, sl=20, tp=40):
    price = mt5.symbol_info_tick(symbol).ask if tipo == "buy" else mt5.symbol_info_tick(symbol).bid
    deviation = 10
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volumen,
        "type": mt5.ORDER_TYPE_BUY if tipo=="buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price - sl*mt5.symbol_info(symbol).point if tipo=="buy" else price + sl*mt5.symbol_info(symbol).point,
        "tp": price + tp*mt5.symbol_info(symbol).point if tipo=="buy" else price - tp*mt5.symbol_info(symbol).point,
        "deviation": deviation,
        "magic": 123456,
        "comment": "Bot Sarah",
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)
    return result

def registrar_resultado(symbol, tipo, resultado, beneficio):
    datos = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            datos = json.load(f)
    datos.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "par": symbol,
        "tipo": tipo,
        "resultado": resultado,
        "beneficio": round(beneficio, 2)
    })
    with open(RESULTS_FILE, "w") as f:
        json.dump(datos, f, indent=4)

async def monitorear_operaciones(app):
    pares = ["EURUSD","GBPUSD","USDJPY"]
    while True:
        for par in pares:
            df = obtener_velas(par, mt5.TIMEFRAME_M1)
            if condiciones_estrategia(df):
                tipo = "buy"  # Ejemplo, en tu estrategia puede decidir buy o sell
                operacion = abrir_operacion(par, tipo)
                if operacion.retcode == mt5.TRADE_RETCODE_DONE:
                    await app.bot.send_message(chat_id=CHAT_ID, text=f"Operación abierta: {par} {tipo}")
                    # Monitorear hasta que cierre por SL/TP
                    ticket = operacion.order
                    while True:
                        pos = mt5.positions_get(ticket=ticket)
                        if not pos:
                            # Cerrada
                            history = mt5.history_orders_get(datetime.now()-pd.Timedelta(minutes=10), datetime.now())
                            for h in history:
                                if h.ticket == ticket:
                                    resultado = "ganada" if h.profit > 0 else "perdida"
                                    registrar_resultado(par, tipo, resultado, h.profit)
                                    await app.bot.send_message(chat_id=CHAT_ID,
                                                               text=f"Operación cerrada: {par} {tipo} | Resultado: {resultado} | Beneficio: {round(h.profit,2)}")
                                    break
                            break
                        await asyncio.sleep(5)
        await asyncio.sleep(30)

# --- TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot Sarah activo. Operando IC Market demo.")

async def resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE,"r") as f:
            datos = json.load(f)
        ultimos = datos[-10:]
        mensaje = "\n".join([f"{d['fecha']} | {d['par']} | {d['tipo']} | {d['resultado']} | {d['beneficio']}" for d in ultimos])
    else:
        mensaje = "No hay resultados aún."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)

# --- INICIALIZAR APP ---
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resultados", resultados))
    asyncio.create_task(monitorear_operaciones(app))
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())