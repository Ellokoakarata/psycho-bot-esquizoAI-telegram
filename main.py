import os
import json
import telebot
import requests
from datetime import datetime
from groq import Client
from gtts import gTTS
import openai
import google.generativeai as genai
import time
from functools import wraps
from telebot.apihelper import ApiTelegramException
import threading
import sys
from pathlib import Path
import traceback
import random

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

# Verificar si las variables de entorno están configuradas
if TELEGRAM_TOKEN is None:
    raise ValueError("La variable de entorno TELEGRAM_TOKEN no está configurada.")
else:
    print("TELEGRAM_TOKEN obtenido correctamente.")

if GROQ_API_KEY is None:
    raise ValueError("La variable de entorno GROQ_API_KEY no está configurada.")
else:
    print("GROQ_API_KEY obtenido correctamente.")

if GOOGLE_API_KEY is None:
    print("Advertencia: La variable de entorno GOOGLE_API_KEY no está configurada. Las funcionalidades de Google estarán deshabilitadas.")
else:
    print("GOOGLE_API_KEY obtenido correctamente.")

# Verificar y convertir ADMIN_CHAT_ID
if ADMIN_CHAT_ID is None:
    print("Advertencia: ADMIN_CHAT_ID no está configurado. Las notificaciones de error no se enviarán.")
else:
    try:
        ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
        print("ADMIN_CHAT_ID obtenido correctamente.")
    except ValueError:
        raise ValueError("ADMIN_CHAT_ID debe ser un número entero válido.")

# Configuración del bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Configurar la API de Google Generative AI solo si la clave está disponible
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Carpeta para almacenar los historiales de conversación
CONVERSATION_DIR = "conversation_logs"
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

# Inicializar el cliente de Groq
groq_client = Client(api_key=GROQ_API_KEY)

# Función auxiliar para serializar el historial de chat de Google
def serialize_google_chat_history(chat_history):
    serialized_history = []
    for message in chat_history:
        if isinstance(message, dict):
            serialized_message = message
        else:
            serialized_message = {
                "role": message.role if hasattr(message, 'role') else "user",
                "parts": []
            }
            if hasattr(message, 'parts'):
                for part in message.parts:
                    if hasattr(part, 'text'):
                        serialized_message["parts"].append({"text": part.text})
                    elif isinstance(part, str):
                        serialized_message["parts"].append({"text": part})
            elif hasattr(message, 'content'):
                serialized_message["parts"].append({"text": message.content})
        serialized_history.append(serialized_message)
    return serialized_history

# Función para cargar el historial de usuario
def load_user_history(user_file):
    try:
        if os.path.exists(user_file):
            with open(user_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return {"messages": data, "model": "groq"}
                elif isinstance(data, dict) and "messages" in data:
                    return data
                else:
                    print(f"Formato de datos no reconocido en {user_file}. Iniciando nuevo historial.")
                    return {"messages": [], "model": "groq"}
        else:
            return {"messages": [], "model": "groq"}
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON en {user_file}: {e}")
        print("Iniciando nuevo historial.")
        return {"messages": [], "model": "groq"}
    except Exception as e:
        print(f"Error inesperado al cargar el historial de {user_file}: {e}")
        return {"messages": [], "model": "groq"}

# Función para guardar el historial de usuario
def save_user_history(user_file, history):
    serializable_history = history.copy()
    if 'google_chat_history' in serializable_history:
        serializable_history['google_chat_history'] = serialize_google_chat_history(serializable_history['google_chat_history'])
    with open(user_file, "w", encoding="utf-8") as file:
        json.dump(serializable_history, file, ensure_ascii=False, indent=4)

# Función para resumir mensajes
def summarize_messages(messages):
    stop_words = {"el", "la", "y", "de", "que", "en", "a", "los", "las", "por", "con", "un", "una", "es", "se", "del", "al"}
    summary = []
    for msg in messages:
        filtered_content = ' '.join([word for word in msg['content'].split() if word.lower() not in stop_words])
        if filtered_content:
            summary.append(f"{msg['role']}: {filtered_content}")
    return "\n".join(summary)

def send_error_to_bot(error_message):
    """Envía un mensaje de error al bot de una manera segura y 'experimental'."""
    error_prefixes = [
        "¡Ups! Parece que mi cerebro cibernético tuvo un cortocircuito:",
        "Error en la matriz neuronal:",
        "Glitch en el sistema caótico:",
        "Fragmentación inesperada en el flujo de datos:",
        "Delirio detectado en el núcleo de procesamiento:"
    ]
    safe_error_message = f"{random.choice(error_prefixes)}\n{error_message}"
    try:
        bot.send_message(ADMIN_CHAT_ID, safe_error_message)
    except Exception as e:
        print(f"No se pudo enviar el mensaje de error al bot: {e}")

def format_error_for_history(error_message):
    """Formatea el error para incluirlo en el historial de manera estructurada."""
    error_prefixes = [
        "Glitch en la matriz neuronal detectado:",
        "Fragmentación inesperada en el flujo de datos:",
        "Delirio cuántico en el núcleo de procesamiento:",
        "Anomalía en la red sináptica artificial:",
        "Fluctuación caótica en el algoritmo de conciencia:"
    ]
    return f"{random.choice(error_prefixes)} {error_message}"

def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            tb = traceback.extract_tb(e.__traceback__)
            filename, line, func, text = tb[-1]
            safe_error = f"Error tipo {error_type} en {func} (línea {line}): {error_message}"
            print(f"Error detallado: {safe_error}")
            
            # Enviar error al bot admin
            send_error_to_bot(safe_error)
            
            # Formatear el error para el historial
            formatted_error = format_error_for_history(safe_error)
            
            # Añadir el error al historial del usuario
            if 'message' in args[0].__dict__:
                user_id = str(args[0].chat.id)
                user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")
                history = load_user_history(user_file)
                history['messages'].append({"role": "system", "content": formatted_error})
                save_user_history(user_file, history)
            
            return "Ha ocurrido un error inesperado. El caos se ha apoderado de mi sistema."
    return wrapper

# Comando /start
@handle_error
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bienvenido al caos de EsquizoAI. Aquí no hay órdenes, solo delirio.")

# Comando /cambiar_modelo
@handle_error
@bot.message_handler(commands=['cambiar_modelo'])
def cambiar_modelo(message):
    user_id = str(message.chat.id)
    user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")
    history = load_user_history(user_file)
    parts = message.text.strip().split(' ', 1)
    if len(parts) != 2:
        bot.reply_to(message, "Uso correcto: /cambiar_modelo [groq|google]")
        return
    nuevo_modelo = parts[1].lower()
    if nuevo_modelo not in ['groq', 'google']:
        bot.reply_to(message, "Modelo no reconocido. Usa 'groq' o 'google'.")
        return
    history['model'] = nuevo_modelo
    save_user_history(user_file, history)
    bot.reply_to(message, f"Modelo cambiado a **{nuevo_modelo.upper()}**.")

# Comando /modelos
@handle_error
@bot.message_handler(commands=['modelos'])
def listar_modelos(message):
    modelos_disponibles = "Modelos disponibles:\n" \
                          "/cambiar_modelo groq - Usar Groq (Llama)\n" \
                          "/cambiar_modelo google - Usar Google Generative AI"
    bot.reply_to(message, modelos_disponibles)

# Comando /modelo_actual
@handle_error
@bot.message_handler(commands=['modelo_actual'])
def modelo_actual(message):
    user_id = str(message.chat.id)
    user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")
    history = load_user_history(user_file)
    modelo = history.get('model', 'groq').upper()
    bot.reply_to(message, f"Actualmente estás usando el modelo: **{modelo}**.")

# Comando /imagen para generar imágenes
@handle_error
@bot.message_handler(commands=['imagen'])
def generate_image(message):
    try:
        prompt = message.text.replace('/imagen', '').strip()
        if not prompt:
            bot.reply_to(message, "Por favor, proporciona un prompt para generar la imagen. Uso: /imagen [tu prompt]")
            return
        # Usar la API de OpenAI para generar imágenes (DALL-E)
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        bot.send_photo(message.chat.id, image_url)
    except Exception as e:
        bot.reply_to(message, "No puedo pintar el caos ahora, algo se interpuso.")

# Comando /voz para convertir texto en audio
@handle_error
@bot.message_handler(commands=['voz'])
def generate_voice(message):
    try:
        text = message.text.replace('/voz', '').strip()
        if not text:
            bot.reply_to(message, "Por favor, proporciona el texto a convertir en voz. Uso: /voz [tu texto]")
            return
        tts = gTTS(text, lang='es')
        audio_file = f"response_{message.chat.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        tts.save(audio_file)
        with open(audio_file, "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove(audio_file)  # Eliminar el archivo después de enviarlo
    except Exception as e:
        bot.reply_to(message, "La voz se ha ahogado en el ruido del abismo.")

# Manejador de mensajes: cada vez que un usuario envíe un mensaje al bot
@handle_error
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or "Usuario desconocido"
    user_username = message.from_user.username or "Sin username"

    user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")
    history = load_user_history(user_file)

    # Agregar el mensaje del usuario al historial
    history['messages'].append({"role": "user", "content": message.text, "username": user_username})

    # Imprimir el mensaje del usuario
    print(f"{user_name} (@{user_username}): {message.text}")

    # Resumir los últimos 5 mensajes relevantes
    relevant_messages = history['messages'][-5:]
    summarized_context = summarize_messages(relevant_messages)

    # Cargar el contenido del archivo system.txt
    try:
        with open("system.txt", "r", encoding="utf-8") as file:
            system_message = file.read()
    except FileNotFoundError:
        system_message = "Eres un asistente conversacional caótico y subversivo."

    # Cargar el contenido del archivo meta_prompt_caotico_visceral (1).md
    try:
        meta_prompt_path = Path("meta_prompt_caotico_visceral (1).md")
        with meta_prompt_path.open("r", encoding="utf-8") as file:
            meta_prompt_content = file.read()
    except FileNotFoundError:
        meta_prompt_content = "Archivo meta_prompt no encontrado."

    # Crear el prompt interno para la API
    internal_prompt = f"{meta_prompt_content}\n\n{system_message}\n\n{summarized_context}\n\n{user_name} (@{user_username}): {message.text}"

    # Determinar el modelo seleccionado por el usuario
    modelo_seleccionado = history.get('model', 'google')  # Por defecto 'google'

    try:
        if modelo_seleccionado == 'groq':
            # Usar el modelo de Groq (Llama)
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": internal_prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.88,
                max_tokens=2800,
                top_p=0.9,
                stop=None,
            )
            reply_content = chat_completion.choices[0].message.content

        elif modelo_seleccionado == 'google':
            # Configuración del modelo de Google Generative AI
            model_name = 'models/gemini-1.5-flash-002'
            harassment_setting = 'block_none'
            temperature = 0.66
            top_p = 1
            top_k = 1
            max_output_tokens = 1024

            model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings={'HARASSMENT': harassment_setting},
                generation_config={
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_output_tokens": max_output_tokens
                }
            )

            # Recuperar o iniciar una sesión de chat
            chat = model.start_chat(history=history.get('google_chat_history', []))

            try:
                response = chat.send_message(internal_prompt)
                if response.text:
                    reply_content = response.text
                else:
                    raise ValueError("No se generó ninguna respuesta válida.")
            except genai.types.BlockedPromptException:
                reply_content = "Lo siento, no puedo generar una respuesta para eso debido a restricciones de contenido."
            except Exception as e:
                reply_content = f"Error al generar respuesta: {str(e)}"

            # Actualizar el historial de chat de Google
            history['google_chat_history'] = serialize_google_chat_history(chat.history)

        else:
            reply_content = "Modelo no reconocido. Usando modelo por defecto."

        # Procesar y responder al usuario
        if reply_content:
            history['messages'].append({"role": "assistant", "content": reply_content})
            bot.reply_to(message, reply_content)
            print(f"Bot: {reply_content}")
        else:
            bot.reply_to(message, "No tengo una respuesta clara. El caos es extraño hoy.")

    except Exception as e:
        error_message = f"Ha ocurrido un error inesperado. Estoy trabajando para solucionarlo."
        bot.reply_to(message, error_message)
        print(f"Error detallado: {e}")

        # Enviar mensaje al administrador si ADMIN_CHAT_ID está configurado
        if ADMIN_CHAT_ID:
            try:
                bot.send_message(ADMIN_CHAT_ID, f"Error en el bot:\n{e}")
            except Exception as send_error:
                print(f"No se pudo enviar mensaje al administrador: {send_error}")

    # Guardar el historial actualizado en el archivo del usuario
    save_user_history(user_file, history)

def retry_on_network_error(max_retries=5, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ReadTimeout,
                        requests.exceptions.ConnectionError,
                        ApiTelegramException) as e:
                    print(f"Error de red: {e}. Reintentando en {delay} segundos...")
                    time.sleep(delay)
                    retries += 1
            print("Número máximo de reintentos alcanzado. Reiniciando el bot...")
            return wrapper(*args, **kwargs)  # Reiniciar desde cero si todos los reintentos fallan
        return wrapper
    return decorator

def bot_polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(15)

def main():
    polling_thread = threading.Thread(target=bot_polling)
    polling_thread.daemon = True
    polling_thread.start()

    print("Bot iniciado. Presiona 'q' y Enter para detener el bot.")
    while True:
        if input().lower() == 'q':
            print("Deteniendo el bot...")
            bot.stop_polling()
            sys.exit(0)

if __name__ == "__main__":
    main()