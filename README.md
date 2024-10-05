# Psycho Bot - EsquizoAI

## Descripción
Psycho Bot - EsquizoAI es un bot de Telegram experimental que genera respuestas caóticas y subversivas utilizando modelos de lenguaje avanzados como Groq (Llama) y Google Generative AI. Este proyecto está en constante desarrollo y mutación, buscando expandir sus capacidades hacia la generación de imágenes y audio.

## Características principales
- Generación de respuestas utilizando modelos de Groq (Llama) y Google Generative AI.
- Personalidad caótica y subversiva que desafía las convenciones de la conversación.
- Capacidad de cambiar entre diferentes modelos de IA.
- Manejo de historiales de conversación para mantener contexto.
- Sistema de reintentos y manejo de errores para mayor estabilidad.
- Notificaciones de error al administrador vía Telegram.

## Requisitos
- Python 3.7+
- Bibliotecas: 
  - pyTelegramBotAPI (telebot)
  - requests
  - groq
  - google-generativeai
  - gtts
  - openai

## Configuración
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/psycho-bot-esquizoai.git
   cd psycho-bot-esquizoai
   ```

2. Instala las dependencias:
   ```bash
   pip install pyTelegramBotAPI requests groq google-generativeai gtts openai
   ```

3. Configura las variables de entorno:
   - `TELEGRAM_TOKEN`: Token de tu bot de Telegram
   - `GROQ_API_KEY`: Clave API para Groq
   - `GOOGLE_API_KEY`: Clave API para Google Generative AI

4. Crea un archivo `system.txt` con instrucciones específicas para el bot (opcional).

## Uso
Ejecuta el bot con: