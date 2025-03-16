"""
Plantilla para detectar volumen del pan y graficarlo.
Usar como referencia o para aportar ideas.

Se guardan las imágenes en un fichero de entrada y se
procesan en un fichero de sálida para luego hacer los cálculos.

Librerías que hay que instalar:
pip install rembg
pip install onnxruntime
"""

import os
from rembg import remove
from PIL import Image
import io
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import re
from datetime import datetime

# from zipfile import ZipFile
from urllib.request import urlretrieve

from IPython.display import YouTubeVideo, display, Image

%matplotlib inline

def create_ouput_data(input_folder, output_folder, processed_folder):
  # Comprobamos que los ficheros existen
  if not os.path.exists(input_folder):
    os.makedirs(input_folder)
    print(f"La carpeta de entrada '{input_folder}' no existe. Se ha creado.")

  if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"La carpeta de salida '{output_folder}' no existe. Se ha creado.")

  if not os.path.exists(processed_folder):
    os.makedirs(processed_folder)
    print(f"La carpeta de procesado '{processed_folder}' no existe. Se ha creado.")

  # Comprobamos que en input_folder hay archivos, si no sale
  if not os.listdir(input_folder):
    print(f"La carpeta de entrada '{input_folder}' está vacía.")
    return

  # Recorremos la carpeta input_folder
  for filename in os.listdir(input_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
      input_path = os.path.join(input_folder, filename)
      img = cv2.imread(input_path)

      print(f"Procesando imagen: {filename}")
      # Tratamos la imagen para quedarnos solo con el objeto (pan)
      img_remove = remove(img)
      output_gray = cv2.cvtColor(img_remove, cv2.COLOR_BGR2GRAY)
      _, mask = cv2.threshold(output_gray, 10, 255, cv2.THRESH_BINARY)
      result = cv2.bitwise_and(img_remove, img_remove, mask=mask)

      # Guardamos la imagen procesada
      output_path = os.path.join(processed_folder, f"processed_{filename}")
      cv2.imwrite(output_path, result)

      print(f"Imagen procesada guardada en: {output_path}")

def extraer_fecha(archivo):
    """Extrae la fecha y hora del nombre del archivo en formato datetime."""
    patron = r'processed_captura_(\d{4}-\d{2}-\d{2}) (\d{2}_\d{2}_\d{2})'
    coincidencia = re.search(patron, archivo)

    if coincidencia:
        fecha_str = coincidencia.group(1)  # YYYY-MM-DD
        hora_str = coincidencia.group(2).replace('_', ':')  # HH:MM:SS
        fecha_hora_str = f"{fecha_str} {hora_str}"
        return datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")

    return datetime.min  # Si no se puede extraer la fecha, devolver un mínimo para evitar errores

def calcular_volumen_entre_imagenes(input_folder, process_folder, output_folder):
    """
    Calcula la diferencia de volumen entre la primera y la última imagen de una carpeta y guarda imágenes procesadas.

    Args:
        input_folder: Ruta a la carpeta que contiene las imágenes sin procesar.
        process_folder: Ruta a la carpeta que contiene las imágenes procesadas sin fondo.
        output_folder: Ruta a la carpeta donde se guardarán las imágenes con la elipse y datos.
    """

    def aislar_transparencias(image):
        if image.shape[2] == 4:
            alpha_channel = image[:, :, 3]
            binary = (alpha_channel > 0).astype(np.uint8) * 255
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        return binary

    def calcular_volumen_a(binary, image, output_path, filename, fecha_str, hora_str, primer_volumen, primera_elipse):
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            print(f"No se encontraron contornos en {filename}")
            return None, None, None, None

        contour = max(contours, key=cv2.contourArea)
        (x, y), (major_axis, minor_axis), angle = cv2.fitEllipse(contour)
        height = minor_axis * 0.6
        a = major_axis / 2
        b = minor_axis / 2
        c = height / 2
        volume = (4 / 3) * np.pi * a * b * c / 2

        output_image = image.copy()
        if primera_elipse:
            cv2.ellipse(output_image, ((int(x), int(y)), (int(primera_elipse[0]), int(primera_elipse[1])), primera_elipse[2]), (0, 0, 255), 2)  # Rojo
        cv2.ellipse(output_image, ((int(x), int(y)), (int(major_axis), int(minor_axis)), angle), (0, 255, 0), 2)  # Verde

        text_dia = f"{fecha_str}"
        text_hora = f"{hora_str}"
        if primer_volumen is not None:
            volumen_relativo = ((volume / primer_volumen) * 100) - 100
        else:
            volumen_relativo = 0
        text_volumen = f"Volumen: {volumen_relativo:.2f}%"
        cv2.putText(output_image, text_dia, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_image, text_hora, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_image, text_volumen, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        output_filepath = os.path.join(output_path, filename)
        cv2.imwrite(output_filepath, output_image)
        # print(f"Imagen guardada en {output_filepath}")

        return volume, a, b, (major_axis, minor_axis, angle)

    volumenes = []
    fechas = []
    eje_a = []
    eje_b = []
    primer_volumen = None
    primera_elipse = None
    
    image_files = sorted([f for f in os.listdir(process_folder) if f.endswith(('.png', '.jpg'))], key=extraer_fecha)
    if not image_files:
        print("No se encontraron imágenes en la carpeta especificada.")
        return

    for i, filename in enumerate(image_files):
        input_filename = filename.replace("processed_", "", 1)
        input_filepath = os.path.join(input_folder, input_filename)
        process_filepath = os.path.join(process_folder, filename)
        image = cv2.imread(input_filepath, cv2.IMREAD_UNCHANGED)
        binary = cv2.imread(process_filepath, cv2.IMREAD_UNCHANGED)
        binary = aislar_transparencias(binary)

        patron = r'processed_captura_(\d{4}-\d{2}-\d{2}) (\d{2}_\d{2}_\d{2})'
        coincidencia = re.search(patron, filename)

        if coincidencia:
            fecha_str = coincidencia.group(1)
            hora_str = coincidencia.group(2).replace('_', ':')

        # Calcular volumen y elipse
        volume, a, b, elipse = calcular_volumen_a(binary, image, output_folder, 
                                                  filename, fecha_str, hora_str,
                                                  primer_volumen, 
                                                  primera_elipse)

        if volume is not None:
            volumenes.append(volume)
            fechas.append(extraer_fecha(filename).strftime("%Y-%m-%d %H:%M:%S"))
            eje_a.append(a)
            eje_b.append(b)
            if primera_elipse is None:
                primera_elipse = elipse
            if primer_volumen is None:
                primer_volumen = volume  # Asignar primer volumen al principio
    
    if volumenes:
        diferencia_volumen = (volumenes[-1] / volumenes[0] * 100) - 100
        print(f"Cambio de volumen entre la primera y la última imagen: {diferencia_volumen:.2f}%")
    else:
        print("No se pudieron procesar las imágenes correctamente.")
    
    return volumenes, fechas

def create_video_from_images(image_folder, video_name="output_video.mp4", fps=5):
    images = [img for img in os.listdir(image_folder) if img.endswith((".png", ".jpg", ".jpeg"))]
    images.sort()  # Sort images for correct order in video

    if not images:
        print("No hay imágenes en el fichero")
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image in images:
        frame = cv2.imread(os.path.join(image_folder, image))
        video.write(frame)
        
        # Agregar pausa de 2 segundos (duplicar el frame 2 * fps veces)
        for _ in range(2 * fps):  
            video.write(frame)

    cv2.destroyAllWindows()
    video.release()
    print(f"Video '{video_name}' creado con éxito.")

create_ouput_data('input_data', 'output_data')

volumenes, fechas = calcular_volumen_entre_imagenes('output_data')

create_video_from_images("output_data")

fechas = [datetime.strptime(f, "%Y-%m-%d %H:%M:%S") for f in fechas]  # Convertir a datetime

if volumenes:
    primer_volumen = volumenes[0]  # Volumen de referencia (primer frame)

    # Calcular el cambio de volumen en porcentaje
    volumenes_porcentaje = [(v / primer_volumen * 100) - 100 for v in volumenes]

    # Graficar
    plt.figure(figsize=(12, 6))
    plt.plot(fechas, volumenes_porcentaje, marker='o', linestyle='-')

    # Agregar etiquetas de porcentaje en cada punto
    for i, txt in enumerate(volumenes_porcentaje):
        plt.text(fechas[i], volumenes_porcentaje[i] + 2, f"{txt:.2f}%", fontsize=8, ha='center', color='black')

    # Personalizar el gráfico
    plt.xlabel("Fecha y Hora")
    plt.ylabel("Cambio de Volumen (%)")
    plt.title("Cambio de Volumen del Pan en Porcentaje")
    plt.grid(True)

    # Ajustar eje X para reflejar tiempos reales
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())  
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M:%S"))
    plt.gcf().autofmt_xdate()  # Rotar etiquetas automáticamente

    # Mostrar el gráfico
    plt.show()
else:
    print("No hay volúmenes para graficar.")
