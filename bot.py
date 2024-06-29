import logging
from telegram.ext import ApplicationBuilder, ContextTypes, filters, MessageHandler
from telegram import Update
import google.generativeai as genai
from pathlib import Path
from config import TOKEN_T, TOKEN_G

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genai.configure(api_key=TOKEN_G)
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
    ]

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
    )

    chat_session = model.start_chat(
    history=[
    ]
    )
    message=update.message
    if message.text:
        response = chat_session.send_message(update.message.text)   
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)
    if message.photo:
        file_id = message.photo[-1].file_id
        file = await context.bot.get_file(file_id)
        file_bytes = await file.download_as_bytearray()
        with open('image.png', 'wb') as f:
            f.write(file_bytes)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Photo downloaded successfully.')
        cookie_picture = {
            'mime_type': 'image/png',
            'data': Path('image.png').read_bytes()
        }
        prompt = message.caption
        response = chat_session.send_message(
            content=[prompt, cookie_picture]
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN_T).build()
    
    echo_handler = MessageHandler(filters.TEXT | filters.PHOTO, echo)
    
    application.add_handler(echo_handler)

    application.run_polling()
