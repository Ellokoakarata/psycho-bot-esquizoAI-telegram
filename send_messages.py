import telebot
import os
from datetime import datetime, timedelta
import time
import keyboard  # Biblioteca para detectar teclas

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("Asegúrate de tener las variables de entorno definidas.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

try:
    while True:
        # Mostrar la hora actual con microsegundos
        ahora = datetime.now()
        print(f"\rLa hora actual es: {ahora.strftime('%H:%M:%S.%f')}", end='')

        # Verificar si se presiona la tecla 's' para detener el reloj e ingresar el mensaje
        if keyboard.is_pressed('s'):
            print("\nDetenido. Ingresa los detalles del mensaje:")

            # Preguntar en cuántos minutos quiere enviar el mensaje
            while True:
                try:
                    minutos_espera = int(input("\n¿En cuántos minutos deseas enviar el mensaje? (Ingresa 0 para salir): "))
                    if minutos_espera == 0:
                        print("Saliendo del programa.")
                        exit(0)
                    break
                except ValueError:
                    print("Por favor, ingresa un valor numérico válido.")
                    continue

            # Preguntar el mensaje a enviar
            mensaje = input("Escribe el mensaje que deseas enviar: ")

            # Calcular la hora objetivo
            ahora = datetime.now()
            hora_objetivo = ahora + timedelta(minutes=minutos_espera)

            # Bucle para calcular el tiempo restante hasta la hora objetivo
            while True:
                ahora = datetime.now()
                tiempo_restante = (hora_objetivo - ahora).total_seconds()

                if tiempo_restante <= 0:
                    break

                # Mostrar el tiempo restante en minutos y segundos
                minutos, segundos = divmod(int(tiempo_restante), 60)
                print(f"\rTiempo restante para enviar el mensaje: {minutos} minutos y {segundos} segundos", end='')

                # Dormir por un segundo antes de volver a calcular el tiempo restante
                time.sleep(1)

            # Enviar el mensaje al llegar a la hora objetivo
            try:
                bot.send_message(ADMIN_CHAT_ID, mensaje)
                print(f"\nMensaje enviado al administrador: {mensaje}")
            except Exception as e:
                print(f"\nError al enviar mensaje: {e}")

        # Dormir por un tiempo antes de actualizar (0.1 segundos para mantenerlo fluido)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario.")
