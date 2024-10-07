
import telebot
import os
from datetime import datetime, timedelta
import time

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5555528445

if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("Asegúrate de tenerlas variables de entorno.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Bucle principal para interactuar con el usuario
while True:
    # Mostrar la hora actual
    ahora = datetime.now()
    print(f"La hora actual es: {ahora.strftime('%H:%M:%S')}")

    # Preguntar en cuántos minutos quiere enviar el mensaje
    try:
        minutos_espera = int(input("¿En cuántos minutos deseas enviar el mensaje? (Ingresa 0 para salir): "))
        if minutos_espera == 0:
            print("Saliendo del programa.")
            break
    except ValueError:
        print("Por favor, ingresa un valor numérico válido.")
        continue

    # Preguntar el mensaje a enviar
    mensaje = input("Escribe el mensaje que deseas enviar: ")

    # Calcular la hora objetivo
    hora_objetivo = ahora + timedelta(minutes=minutos_espera)

    # Bucle para calcular el tiempo restante hasta la hora objetivo
    while True:
        ahora = datetime.now()
        tiempo_restante = (hora_objetivo - ahora).total_seconds()

        if tiempo_restante <= 0:
            break

        # Mostrar el tiempo restante en minutos y segundos
        minutos, segundos = divmod(int(tiempo_restante), 60)
        print(f"Tiempo restante para enviar el mensaje: {minutos} minutos y {segundos} segundos")

        # Dormir por un segundo antes de volver a calcular el tiempo restante
        time.sleep(1)

    # Enviar el mensaje al llegar a la hora objetivo
    try:
        bot.send_message(ADMIN_CHAT_ID, mensaje)
        print(f"Mensaje enviado al administrador: {mensaje}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

