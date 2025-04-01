import cv2
import os
import time
import numpy as np
from datetime import datetime,timedelta
import logging
from rembg import remove

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
        self.primera_elipse = None
        self.primera_area = None
        

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
                    output = self.calcular_volumen(frame) # calcular el volumen de la imagen

                    if output == False:
                        logging.warning("No se ha detectado el pan en la imagen")
                    else:
                        frame = output

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
    
    def calcular_volumen(self,image):
        fecha_str = datetime.now().strftime("%Y-%m-%d")
        hora_str = datetime.now().strftime("%H:%M:%S")

        # eliminamos el fondo
        pan_png = remove(image)
        pan_cv = cv2.cvtColor(np.array(pan_png), cv2.COLOR_RGB2BGR)
        pan_gray = cv2.cvtColor(pan_cv, cv2.COLOR_BGR2GRAY) 
        # aplicamos umbralizacion y detectamos contornos
        _,treshold = cv2.threshold(pan_gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(treshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return False
        
        # creamos la elipse
        contour = max(contours, key=cv2.contourArea)
        elipse = cv2.fitEllipse(contour)

        # calculamos el area de la elipse
        (x, y), (major_axis, minor_axis), angle = elipse
        height = minor_axis * 0.6
        a = major_axis / 2
        b = minor_axis / 2
        c = height / 2
        volume = (4 / 3) * np.pi * a * b * c / 2    

        output_image = image.copy()

        text_volumen = ""
        if self.primera_elipse is None:
            self.primera_elipse = elipse
            self.primera_area = volume

            cv2.ellipse(output_image, self.primera_elipse, (0, 0, 255), 2)  # Azul
            text_volumen = "Volumen: 0%"
            cv2.putText(output_image, text_volumen, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        else:

            # pintado de la primera elipse
            cv2.ellipse(output_image, self.primera_elipse, (0, 0, 255), 2)  # Rojo

            # pintado de la segunda elipse
            cv2.ellipse(output_image, elipse, (0, 255, 0), 2)  # Verde

            # calculo del crecimiento
            crecimiento = ((volume / self.primera_area) * 100) - 100
            text_volumen = f"Volumen: {crecimiento:.2f}%"

            cv2.putText(output_image, text_volumen, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        text_dia = f"{fecha_str}"
        text_hora = f"{hora_str}"
        cv2.putText(output_image, text_dia, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_image, text_hora, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return output_image
           