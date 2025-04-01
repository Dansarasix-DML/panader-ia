import requests
from telegram import  Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackContext
from photo import Capturadora
import threading
import logging as tele
import logging
import io
from datetime import datetime
import config.credentials

tele.basicConfig(
    filename="telegram_bot.log",  # Nombre del archivo de log
    level=tele.INFO,  # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha
)

logging.basicConfig(
    filename="server.log",  # Nombre del archivo de log
    level=logging.INFO,  # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del mensaje
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha
)


class TelegramBot():

    def __init__(self,capturadora:Capturadora):
        self.TOKEN = config.credentials.TOKEN
        self.CHAT_ID = config.credentials.CHAT_ID
        self.URL_M = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
        self.capturadora = capturadora

    async def iniciar_captura(self,update:Update, context:CallbackContext):
        err_msg = "Error al iniciar la captura de imagenes, argumentos inválidos\n" \
                    "Ejemplo de ejecución:\n" \
                    "/iniciar_captura --intervalo <n> --tipo_pan <pan>\n" \
                    "Donde <n> es el intervalo de tiempo en minutos y <pan> es el tipo de pan a capturar"
        
        logging.info("Orden del bot de iniciado de capturas de imagenes")

        if context.args:
            if len(context.args) == 4:    

                if (context.args[0] == "--intervalo" and context.args[2] == "--tipo_pan"):

                    self.capturadora.capturando = True
                    self.capturadora.interval = int(context.args[1])
                    self.capturadora.tipo_pan = context.args[3]

                    logging.info(f"Captura iniciada con intervalo de {self.capturadora.interval} minutos y tipo de pan {self.capturadora.tipo_pan}")
                    await update.message.reply_text(f"Iniciando captura de imagenes para el pan {self.capturadora.tipo_pan} cada {self.capturadora.interval} minutos") 
                    threading.Thread(target=self.capturadora.capturar_fotos_automaticas).start()

                else:
                    logging.error("Proceso de captura fallido, los argumentos dentro del diccionario son incorrectos")
                    await update.message.reply_text(err_msg)
                
                
                
        else:
            logging.error("Proceso de captura fallido, no se han pasado argumentos")

            msg = "Error al iniciar la captura de imagenes, necesito argumentos\n" \
            "Ejemplo de ejecución:\n" \
            "/iniciar_captura --intervalo <n> --tipo_pan <pan>\n" \
            "Donde <n> es el intervalo de tiempo en minutos y <pan> es el tipo de pan a capturar si el pan a poner tiene un nombre compuesto hay que ponsr su valor entre comillas ej: \"pan de maíz\""

            await update.message.reply_text(msg)

            
    async def detener_captura(self,update:Update, context:CallbackContext):
        logging.info("Orden del bot de cancelacion de captura de imagenes")
        await update.message.reply_text("Deteniendo captura de imagenes automaticas")
        self.capturadora.capturando = False
        self.capturadora.first_img = None
        self.capturadora.img_now = None
        self.capturadora.imgs = 0
        self.capturadora.interval = 5
        self.capturadora.tipo_pan = None    

    async def get_image_now(self,update:Update, context:CallbackContext):
        logging.info("Orden del bot de obtener imagen actual")
        if self.capturadora.img_now is None:
            await update.message.reply_text("No hay ninguna imagen capturada")
        else:
            image_stream = io.BytesIO(self.capturadora.img_now)
            image_stream.seek(0)

        await update.message.reply_photo(photo=image_stream,caption="Imagen actual capturada")

    async def get_images(self,update:Update, context:CallbackContext):
        logging.info("Orden del bot de obtener la comparacion de imagenes")
        if self.capturadora.first_img is None or self.capturadora.img_now is None:
            await update.message.reply_text("No hay imagenes capturadas")
        else:
            image_stream1 = io.BytesIO(self.capturadora.first_img)
            image_stream1.seek(0)
            image_stream2 = io.BytesIO(self.capturadora.img_now)
            image_stream2.seek(0)

            await update.message.reply_photo(photo=image_stream1,caption="Primera imagen capturada")
            await update.message.reply_photo(photo=image_stream2,caption="Ultima imagen capturada")
    async def status(self,update:Update, context:CallbackContext):
        logging.info("Orden del bot de estado de la raspberry")
        if(self.capturadora.capturando):
            msg = "Estado de la raspberry: Capturando imágenes\n" \
            f"Frecuencia de capturas: {self.capturadora.interval} minutos\n" \
            f"Próxima captura: {self.capturadora.next_cap.strftime('%H:%M:%S')}\n" \
            f"Tiempo restante para la próxima captura {(self.capturadora.next_cap - datetime.now())}\n" \
            f"Tipo de pan: {self.capturadora.tipo_pan}\n" \
            f"Imagenes capturadas: {self.capturadora.imgs}\n" \
            f"Carpeta de imagenes: {self.capturadora.image_folder}\n"
            await update.message.reply_text(msg)
        else:
            msg = "Estado de la raspberry: Esperando orden de captura de imágenes\n" \
            "Se requiere de activación por interfaz web o por comando de telegram\n" \
            "Comando /iniciar_captura --intervalo <n> --tipo_pan <pan>" 
            await update.message.reply_text(msg)

    async def help(self,update:Update, context:CallbackContext):
        logging.info("Orden del bot para mostrar sus comandos disponibles")
        msg = "Comandos disponibles:\n" \
        "/iniciar_captura --intervalo <n> --tipo_pan <pan>: Inicia la captura de imagenes automaticas\n" \
        "/detener_captura: Detiene la captura de imagenes automaticas\n" \
        "/get_image_now: Obtiene la imagen actual\n" \
        "/get_images: Obtiene todas las imagenes capturadas\n" \
        "/status: Muestra el estado actual de la raspberry\n" \
        "/help: Muestra los comandos disponibles"
        await update.message.reply_text(msg)

    def main(self):
        app = Application.builder().token(self.TOKEN).build()

        # comandos hábiles del bot
        app.add_handler(CommandHandler("iniciar_captura", self.iniciar_captura))
        app.add_handler(CommandHandler("detener_captura", self.detener_captura))
        app.add_handler(CommandHandler("get_image_now", self.get_image_now))
        app.add_handler(CommandHandler("get_images", self.get_images))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("help", self.help))
        
        requests.post(self.URL_M, data={"chat_id": self.CHAT_ID, "text": "Estoy listo para ejecutar los comandos para los que me habeis preparado"})

        app.run_polling()
