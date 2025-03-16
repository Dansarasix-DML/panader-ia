from flask import Flask, render_template
from flask_socketio import SocketIO
from photo import Capturadora
from flask_cors import CORS
import eventlet
import eventlet.wsgi
import threading

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

CORS(app, resources={r"/*": {"origins": "http://192.168.127.138:5002"}})
camara = Capturadora()

@app.route('/')

def index():
    return render_template("index.html")

@socketio.on("iniciar_captura")
def iniciar_captura(data):

    if not camara.capturando:
        camara.capturando = True
        camara.interval = data.get("interval", 5)
        camara.tipo_pan = data.get("tipo_pan", "barra")
        threading.Thread(target=camara.capturar_fotos_automaticas).start()

@socketio.on("detener_captura")
def detener_captura():
    camara.capturando = False
    camara.imgs = []
    camara.img_now = None
    camara.interval = 5
    camara.tipo_pan = None

@socketio.on("heartbeat")
def heartbeat():
    print(f"Informacion del objeto: camara:{camara.capturando}\nintervalo:{camara.interval}\npan:{camara.tipo_pan}")
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
        socketio.emit("nuevas_imagenes", camara.imgs)

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('192.168.127.138', 5002)), app)
    #socketio.run(app, host='192.168.127.138', debug=True, port=5002, allow_unsafe_werkzeug=True)
