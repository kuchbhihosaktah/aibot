
# m.py
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from moviepy.editor import ImageClip
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image

# ====== Apna bot token yahan daale ======
TOKEN = "8386912250:AAHWppIHrXHpG8lQuZ7l3xkO4AjMUkIkhZg"

# Setup Stable Diffusion Img2Img (GPU required)
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16
)
pipe = pipe.to("cuda")  # GPU

# Temporary storage for user images
user_images = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello! Send me an image first. Then use /prompt <description> to modify it and convert to video."
    )

def handle_image(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = photo.get_file()
    file_path = f"{user_id}_input.jpg"
    file.download(file_path)
    user_images[user_id] = file_path
    update.message.reply_text("Image received! Now send /prompt <your description>.")

def handle_prompt(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_images:
        update.message.reply_text("Please send an image first!")
        return

    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("Please provide a prompt. Example: /prompt a sunset over mountains")
        return

    update.message.reply_text("Generating modified image... ⏳")

    # Load input image
    init_image = Image.open(user_images[user_id]).convert("RGB")
    
    # Generate AI-modified image
    image = pipe(prompt=prompt, image=init_image, strength=0.7, guidance_scale=7.5).images[0]
    output_image_path = f"{user_id}_output.png"
    image.save(output_image_path)

    # Convert to video
    video_path = f"{user_id}_output_video.mp4"
    clip = ImageClip(output_image_path, duration=5)
    clip.write_videofile(video_path, fps=24)

    # Send video
    update.message.reply_video(video=open(video_path, "rb"))

    # Cleanup
    os.remove(user_images[user_id])
    os.remove(output_image_path)
    os.remove(video_path)
    user_images[user_id] = None

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.PHOTO, handle_image))
    dp.add_handler(CommandHandler("prompt", handle_prompt))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
