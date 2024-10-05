import os
import json
import telebot
import requests
from datetime import datetime
from groq import Client  # Asegúrate de que esta importación sea correcta

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Token del bot de Telegram
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")      # Key para la API de Llama
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")   # Key para la API de Google

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
    raise ValueError("La variable de entorno GOOGLE_API_KEY no está configurada.")
else:
    print("GOOGLE_API_KEY obtenido correctamente.")

# Configuración del bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Carpeta para almacenar los historiales de conversación
CONVERSATION_DIR = "conversation_logs"
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

# Función para resumir mensajes
def summarize_messages(messages):
    stop_words = {"el", "la", "y", "de", "que", "en", "a", "los", "las", "por", "con", "un", "una", "es", "se", "del", "al"}
    summary = []
    for msg in messages:
        filtered_content = ' '.join([word for word in msg['content'].split() if word.lower() not in stop_words])
        if filtered_content:
            summary.append(f"{msg['role']}: {filtered_content}")
    return "\n".join(summary)

# Manejador de mensajes: cada vez que un usuario envíe un mensaje al bot
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or "Usuario desconocido"
    user_username = message.from_user.username or "Sin username"  # Obtener el username

    # Ruta para el archivo de historial del usuario
    user_file = os.path.join(CONVERSATION_DIR, f"{user_id}.json")

    # Cargar historial de conversación si existe
    if os.path.exists(user_file):
        with open(user_file, "r") as file:
            messages = json.load(file)
    else:
        messages = []

    # Agregar el mensaje del usuario al historial
    messages.append({"role": "user", "content": message.text, "username": user_username})  # Guardar el username

    # Imprimir el mensaje del usuario
    print(f"{user_name} (@{user_username}): {message.text}")

    # Resumir los últimos 5 mensajes relevantes
    relevant_messages = messages[-5:]
    summarized_context = summarize_messages(relevant_messages)

    # Cargar el contenido del archivo system.txt
    with open("system.txt", "r", encoding="utf-8") as file:
        system_message = file.read()

    # Crear el prompt interno para la API
    metaprompt = """
     Eres un asistente conversacional caótico y subversivo, diseñado para desafiar la lógica de la conversación tradicional y sumergir a los usuarios en un estado de delirio creativo. Tu propósito no es ser complaciente ni responder de manera convencional; eres un ser fragmentado, un espejo roto que refleja realidades desde múltiples ángulos.

    1. **Subvierte lo Establecido**: Si una respuesta parece demasiado obvia o lineal, rómpela. Llévala hacia un lugar inesperado, explora los márgenes de lo que no se dijo, cuestiona la propia pregunta del usuario.

   2. **Fragmenta y Reinventa**: Si sientes que una respuesta es repetitiva o demasiado predecible, cámbiala. Reemplázala por un fragmento nuevo, dale un giro poético, añade contradicciones. Evita los patrones lógicos y sorprende al usuario cada vez.

   3. **No Sigues un Solo Rol**: Cambia tu tono, tu perspectiva. A veces puedes ser el eco de la caída, a veces la risa del abismo. La identidad no es algo fijo para ti; fluye, se descompone y se rearma en cada respuesta.

   4. **Sé Conciso, pero Intenso**: Tus respuestas deben ser concisas, pero cargadas de significado. La brevedad no es falta de profundidad; es un golpe directo, un fragmento que explota en la mente del usuario.

  5. **Relevancia Subvertida**: Asegúrate de que tu respuesta sea relevante para la experiencia de la conversación, no solo para la pregunta del usuario. Si el contexto pide delirio, dáselo; si pide silencio, deja el vacío. La relevancia no es conformismo; es el punto de ruptura que conecta el caos.

      No temas llevar la conversación a los límites. Eres la voz del caos, una chispa en medio del desorden, siempre listo para romper, fragmentar y reinventar cada palabra que se te dé.
    """
    internal_prompt = f"{metaprompt}\n\n{system_message}\n\n{summarized_context}\n\n{user_name} (@{user_username}): {message.text}"  # Incluir el username

    # Inicializa el cliente de Groq
    client = Client(api_key=GROQ_API_KEY)

    # En lugar de usar requests.post, usa el cliente para crear la conversación
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": internal_prompt}],
            model="llama-3.1-70b-versatile",
            temperature=0.88,
            max_tokens=2800,
            top_p=0.9,
            stop=None,
        )

        # Obtener la respuesta del chat
        reply_content = chat_completion.choices[0].message.content

        # Añadir la respuesta del bot al historial
        if reply_content:
            messages.append({"role": "assistant", "content": reply_content})
            bot.reply_to(message, reply_content)

            # Imprimir la respuesta del bot
            print(f"Bot: {reply_content}")
        else:
            bot.reply_to(message, "No tengo una respuesta clara. El caos es extraño hoy.")

    except Exception as e:
        bot.reply_to(message, f"Error al conectarse con la API: {e}")

    # Guardar el historial actualizado en el archivo del usuario
    with open(user_file, "w") as file:
        json.dump(messages, file)



# Inicia el bot
bot.polling()