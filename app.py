from flask import Flask, render_template
from flask_socketio import SocketIO
from photo import capturar_fotos_automaticas
from flask_cors import cross_origin

app = Flask(__name__)
socketio = SocketIO(app)

#CORS(app)
#CORS(app, resources={r"/*": {"origins": "http://192.168.127.138:5002"}})

capturando = False

@app.route('/')
@cross_origin(origins="http://192.168.127.138/")
def index():
    return render_template("index.html")

@socketio.on("iniciar_captura")
def iniciar_captura(data):
    global capturando
    if not capturando:
        tipo_pan = data.get("tipo_pan", "barra")
        interval = data.get("interval", 5)
        socketio.start_background_task(target=capturar_fotos_automaticas, socketio=socketio, interval=interval)

@socketio.on("detener_captura")
def detener_captura():
    global capturando
    capturando = False

if __name__ == "__main__":
    socketio.run(app, host='192.168.127.138', debug=True, port=5002)
