import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import streamlit as st

# This adds visible status logs to your terminal screen
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Received a /hello command!") # Visible in your terminal
    #add help here
    await update.message.reply_text(f'Hello {update.effective_user.first_name}!')



if __name__ == '__main__':
    print("Starting bot... Press Ctrl+C to stop.")
    
    # PUT YOUR ACTUAL TOKEN HERE
    app = ApplicationBuilder().token("8912754717:AAGPBWe5bS4WzQJ6HlqWeTCmzAlvB3ZzTvQ").build()
    
    app.add_handler(CommandHandler("start", hello))
    
    app.run_polling()
