import os
from flask import Flask
from threading import Thread
from bot import main as bot_main

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot Sarah activo ✅"

if __name__ == "__main__":
    # Ejecutar bot en un hilo separado para que Flask no se bloquee
    Thread(target=bot_main).start()
    
    # Puerto que Render asigna automáticamente
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)