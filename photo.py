import cv2
import os
import time
from flask_socketio import emit

# Carpeta donde se guardarán las imágenes
IMAGE_FOLDER = "capturas"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

capturando = False  # Variable de control

def capturar_fotos_automaticas(socketio, interval=5):
    global capturando
    capturando = True  # Activar captura

    try:
        while capturando:
            cap = cv2.VideoCapture(0)  # Iniciar la cámara

            if not cap.isOpened():
                print("No se pudo abrir la camara")
                return
            
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar imagen")
                break

            counter = 0
            image_path = os.path.join(IMAGE_FOLDER, f"captura_{counter}.jpg")

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
