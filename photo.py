import cv2
import os
import time
from datetime import datetime
from flask_socketio import emit

# Carpeta donde se guardarán las imágenes
IMAGE_FOLDER = "/home/raspberry/media/raspberry/D072-7D9A/capturas"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

capturando = False  # Variable de control

def capturar_fotos_automaticas(socketio, interval=5):
    global capturando
    capturando = True  # Activar captura

    try:
        counter = 0
        while capturando:
            cap = cv2.VideoCapture(0)  # Iniciar la cámara

            if not cap.isOpened():
                print("No se pudo abrir la camara")
                return
            
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar imagen")
                break
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            image_path = os.path.join(IMAGE_FOLDER, f"captura_{timestamp}.jpg")

            frame = frame[::-1]  # Invertir imagen
            cv2.imwrite(image_path, frame)  # Guardar imagen

            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
                socketio.emit("nueva_imagen", img_bytes)  # Enviar imagen al frontend
 
            cap.release()
            print("Camara liberada")
            counter = counter + 1
            time.sleep(int(interval) * 10)  # Esperar 2 segundos antes de la siguiente captura

    finally:
        capturando = False
