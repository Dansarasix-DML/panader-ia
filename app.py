from flask import Flask, render_template
from flask_socketio import SocketIO
from photo import Capturadora
from bot_telegram import TelegramBot
from flask_cors import CORS
import eventlet
import eventlet.wsgi
import asyncio
import threading
import logging
import os
import config.credentials

ADDRESS = config.credentials.IP_RASPBERRY

logging.basicConfig(
    filename="server.log",  # Nombre del archivo de log
    level=logging.INFO,  # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha
)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

CORS(app, resources={r"/*": {"origins": f"http://{ADDRESS}:5002"}})
camara = Capturadora()
bot = TelegramBot(camara)

@app.route('/')

def index():
    return render_template("index.html")

@socketio.on("iniciar_captura")
def iniciar_captura(data):

    if not camara.capturando:
        camara.capturando = True
        camara.interval = data.get("interval", 5)
        camara.tipo_pan = data.get("tipo_pan", "barra")
        logging.info(f"Captura iniciada con intervalo de {camara.interval} minutos y tipo de pan {camara.tipo_pan}")
        # Hilo secundario que ejecuta la capturradora de fotos
        threading.Thread(target=camara.capturar_fotos_automaticas).start()

@socketio.on("detener_captura")
def detener_captura():
    logging.info(f"Captura detenida, se van a resetear los valores a nulos, hasta que la camara no se apague se recomienda no iniciar una nueva captura")
    camara.capturando = False
    camara.first_img = None
    camara.img_now = None
    camara.interval = 5
    camara.tipo_pan = None

@socketio.on("heartbeat")
def heartbeat():
    logging.info(f"Recarga de la web detectada")
    if(camara.capturando):
        socketio.emit("capturando", True)
        socketio.emit("intervalo", camara.interval)
    else:
        socketio.emit("capturando", False)

@socketio.on("get_image_now")
def image_now():
    if camara.capturando:
        socketio.emit("nueva_imagen", camara.img_now)

@socketio.on("get_images")
def get_images():
    if camara.capturando:
        panes = [camara.img_now, camara.first_img]
        socketio.emit("nuevas_imagenes", panes)


def run_flask():
    logging.info(f"Servidor Flask iniciado en {ADDRESS}:5002")
    eventlet.wsgi.server(eventlet.listen((ADDRESS, 5002)), app)

if __name__ == "__main__":
    logging.info(f"Servidor iniciado con la direccion IP {ADDRESS}")
    logging.info(f"Puerto 5002")
    logging.info(f"Los logs se registran en el fichero {os.getcwd()}/server.log")
    
     # Hilo secundario que ejeucuta el servidor
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Hilo principal que ejecuta el bot de telegram
    asyncio.run(bot.main())
