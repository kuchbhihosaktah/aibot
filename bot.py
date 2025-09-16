from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import requests
from io import BytesIO

# Telegram Bot Token
TOKEN = "8386912250:AAHWppIHrXHpG8lQuZ7l3xkO4AjMUkIkhZg"

# Hugging Face API Token
HF_TOKEN = "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"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a prompt, and I will generate an AI image for you.")

def generate_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None

def handle_message(update: Update, context: CallbackContext):
    prompt = update.message.text
    update.message.reply_text("Generating image... ⏳")
    
    image_data = generate_image(prompt)
    if image_data:
        update.message.reply_photo(photo=image_data)
    else:
        update.message.reply_text("Failed to generate image. Try again!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
