"""
Plantilla para detectar volumen del pan y graficarlo.
Usar como referencia o para aportar ideas.

Se guardan las imágenes en un fichero de entrada y se
procesan en un fichero de sálida para luego hacer los cálculos.
"""

def create_ouput_data(input_folder, output_folder):
  # Comprobamos que los ficheros existen
  if not os.path.exists(input_folder):
    os.makedirs(input_folder)
    print(f"La carpeta de entrada '{input_folder}' no existe. Se ha creado.")
    return
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"La carpeta de salida '{output_folder}' no existe. Se ha creado.")
    return

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
      output_path = os.path.join(output_folder, f"processed_{filename}")
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

def calcular_volumen_entre_imagenes(output_folder):
    """
    Calcula la diferencia de volumen entre la primera y la última imagen de una carpeta.

    Args:
        output_folder: Ruta a la carpeta que contiene las imágenes procesadas.
    """

    def aislar_transparencias(image):
      # Si tiene canal alfa (transparencia), aislar la parte visible
      if image.shape[2] == 4:
          alpha_channel = image[:, :, 3]
          binary = (alpha_channel > 0).astype(np.uint8) * 255
      else:
          gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

      return binary

    def calcular_volumen_a(binary, image):
      # Encontrar los contornos del pan
      contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      contour = max(contours, key=cv2.contourArea)

      # Ajustar un elipse alrededor del contorno
      (x, y), (major_axis, minor_axis), angle = cv2.fitEllipse(contour)

      # Aproximar la altura como un 60% del eje menor (ajustable según la vista)
      height = minor_axis * 0.6

      # Calcular el volumen de la mitad del elipsoide
      a = major_axis / 2  # Eje mayor (largo del pan)
      b = minor_axis / 2  # Eje menor (ancho del pan)
      c = height / 2      # Altura (estimada)

      volume = (4 / 3) * np.pi * a * b * c / 2

      print(f"Volumen estimado del pan (mitad del elipsoide): {volume:.2f} píxeles cúbicos")
      return volume, a, b

    volumenes = []  # Almacena los volúmenes de cada imagen
    fechas = []
    eje_a = []
    eje_b = []
    primer_volumen = None  # Variable para almacenar el primer volumen
    ultimo_volumen = None  # Variable para almacenar el último volumen

    # Lista de imágenes con la extensión .png o .jpg
    image_files = [f for f in os.listdir(output_folder) if f.endswith(('.png', '.jpg'))]

    # Ordena los archivos basándose en la fecha extraída
    image_files = sorted(image_files, key=extraer_fecha)

    # Comprueba si se encontraron imágenes
    if not image_files:
        print("No se encontraron imágenes .png o .jpg en la carpeta especificada.")
        return  # Salir de la función si no hay imágenes


    for filename in image_files:
        filepath = os.path.join(output_folder, filename)
        image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

        # Reutilizamos la función aislar_transparencias para aislar las partes no transparentes
        binary = aislar_transparencias(image)
        # Call the original volume calculation function (now renamed)
        volume, a, b = calcular_volumen_a(binary, image)
        # print(f"Imagen {filepath}: {volume}")

        volumenes.append(volume)
        fechas.append(extraer_fecha(filename).strftime("%Y-%m-%d %H:%M:%S"))
        eje_a.append(a)
        eje_b.append(b)

        if primer_volumen is None:
            primer_volumen = volume

    ultimo_volumen = volumenes[-1]  # El último volumen es el último de la lista

    # Calcula el cambio de volumen relativo al primer volumen
    if primer_volumen is not None and ultimo_volumen is not None:
      diferencia_volumen = ((ultimo_volumen / primer_volumen) * 100) - 100
      print(f"Cambio de volumen entre la primera y la última imagen: {diferencia_volumen:.2f}%")
    else:
      print("No se encontraron imágenes en la carpeta especificada o no se pudieron procesar.")

    return volumenes, fechas

create_ouput_data('input_data', 'output_data')

volumenes, fechas = calcular_volumen_entre_imagenes('output_data')

if volumenes:
    primer_volumen = volumenes[0]  # Volumen de referencia (primer frame)

    # Calcular el cambio de volumen en porcentaje
    volumenes_porcentaje = [(v / primer_volumen * 100) - 100 for v in volumenes]

    # Graficar
    plt.figure(figsize=(12, 6))
    plt.plot(fechas, volumenes_porcentaje, marker='o', linestyle='-')

    # Personalizar el gráfico
    plt.xlabel("Fecha y Hora")
    plt.ylabel("Cambio de Volumen (%)")
    plt.title("Cambio de Volumen del Pan en Porcentaje")
    plt.grid(True)
    plt.xticks(rotation=90)  # Rotar las etiquetas del eje X para mejor visibilidad

    # Mostrar el gráfico
    plt.show()
else:
    print("No hay volúmenes para graficar.")
