import cv2
import os
import time

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
        
        cap = cv2.VideoCapture(0)  # Iniciar la cámara

        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return
        
        try:
            while self.capturando:
                ret, frame = cap.read()
                if not ret:
                    print("Error al capturar imagen")
                    break

                timestamp = int(time.time())
                image_path = os.path.join(self.image_folder, f"captura_{timestamp}.png")

                cv2.imwrite(image_path, frame)  # Guardar imagen
                with open(image_path, "rb") as img_file:
                    img_bytes = img_file.read()
                    self.img_now = img_bytes
                    self.imgs.append(img_bytes)
                time.sleep(int(self.interval) * 60)  # Esperar 2 segundos antes de la siguiente captura
            if not self.capturando:
                print("Camara detenida")
                cap.release()
        finally:
            cap.release()
            print("Cámara liberada")