import cv2
import os
import time
from datetime import datetime
import logging

logging.basicConfig(
    filename="server.log",  # Nombre del archivo de log
    level=logging.DEBUG,  # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha
)

class Capturadora:

    def __init__(self,capturando=False,interval=5,tipo_pan=None):
        self.capturando = capturando
        self.interval = interval
        self.tipo_pan = tipo_pan
        self.img_now = None
        self.imgs = []
        self.image_folder = "/home/raspberry/media/raspberry/D072-7D9A/capturas"
        

    def capturar_fotos_automaticas(self):
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
        logging.info("Iniciando camara")
        cap = cv2.VideoCapture(0)  # Iniciar la cámara
        logging.info("Camara iniciada si en la interfaz no se muestra la imagen recargue la web")
        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return
        
        try:
            while self.capturando:
                ret, frame = cap.read()
                if not ret:
                    print("Error al capturar imagen")
                    break
                fecha = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
                image_path = os.path.join(self.image_folder, f"captura_{fecha}.png")
                frame = frame[::-1] # invertir la imagen
                cv2.imwrite(image_path, frame)  # Guardar imagen
                with open(image_path, "rb") as img_file:
                    img_bytes = img_file.read()
                    self.img_now = img_bytes
                    self.imgs.append(img_bytes)
                    logging.info(f"Nueva imagen generada, nombre del archivo captura_{fecha}.png")
                time.sleep(int(self.interval) * 60)  # Esperar 2 segundos antes de la siguiente captura
        finally:
            logging.info("Camara detenida, el servidor esta preparado para iniciar una nueva captura")
            cap.release()
           