import cv2
import os
import time
from datetime import datetime,timedelta
import logging

logging.basicConfig(
    filename="server.log",  # Nombre del archivo de log
    level=logging.INFO,  # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha
)

class Capturadora:

    def __init__(self,capturando=False,interval=5,tipo_pan=None):
        self.capturando = capturando
        self.interval = interval
        self.tipo_pan = tipo_pan
        self.img_now = None
        self.first_img = None
        self.next_cap = None
        self.imgs = 0
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

        date_now = datetime.now()
        date_str = date_now.strftime("%H:%M:%S")
        date_next_str = date_str
        
        try:
            while self.capturando:
                if(date_str==date_next_str):
                    if not cap.isOpened():
                        logging.info("Preparando camara para realizar una captura")
                        cap = cv2.VideoCapture(0)
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
                        if self.first_img is None:
                            self.first_img = img_bytes
                        self.img_now = img_bytes
                        self.imgs += 1
                        logging.info(f"Nueva imagen generada, nombre del archivo captura_{fecha}.png")
                    cap.release()
                    logging.info("Camara apagada esperando a la siguiente captura")
                    date_next = date_now + timedelta(minutes=self.interval)
                    date_next_str = date_next.strftime("%H:%M:%S")
                    self.next_cap = date_next
                    logging.info(f"La siguiente captura se realizara en la siguiente hora {date_next}")
                date_now = datetime.now()
                date_str = date_now.strftime("%H:%M:%S")

        finally:
            logging.info("Camara detenida, el servidor esta preparado para iniciar una nueva captura")
            cap.release()
           