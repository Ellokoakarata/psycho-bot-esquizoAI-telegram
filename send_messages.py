import telebot
import os

# Prueba si recoges correctamente las variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("Asegúrate de que TELEGRAM_TOKEN y ADMIN_CHAT_ID estén definidos en las variables de entorno.")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Enviar mensaje al administrador
def notify_admin(message):
    try:
        bot.send_message(ADMIN_CHAT_ID, message)
        print(f"Mensaje enviado al administrador: {message}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

# Ejemplo de uso
notify_admin("Hola admin, el bot tiene permisos para enviar mensajes.")
