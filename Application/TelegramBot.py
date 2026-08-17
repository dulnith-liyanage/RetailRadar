import logging
import os
import pandas as pd
from groq import Groq
from telegram import Update
import streamlit as st
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from utils import clean_data, get_raw_data, get_segment_summary, get_sales_forecast
import threading

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

GROQ_API_KEY = st.secrets['API_KEY']
TELEGRAM_BOT_TOKEN = st.secrets['TELE_BOT_API']

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ API key. Set the API_KEY environment variable.")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Missing Telegram bot token. Set the TELE_BOT_API environment variable.")

client = Groq(api_key=GROQ_API_KEY)

# --- Your dataset preparation code here (unchanged) ---
raw_df, _ = get_raw_data()
df = clean_data(raw_df)
# ... all your analysis and prompt building code remains the same ...

SYSTEM_PROMPT = build_system_prompt()

def generate_reply(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or "I could not generate a response."

def split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks, remaining = [], text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! Send me a retail question and I’ll reply with an analysis from the Retail Radar dataset."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Ask about revenue, districts, products, customer segments, day-of-week trends, or hourly trends."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not update.message.text:
        return
    prompt = update.message.text.strip()
    if not prompt:
        return
    logging.info("Received Telegram message: %s", prompt)
    try:
        reply = generate_reply(prompt)
    except Exception as exc:
        logging.exception("Failed to generate Telegram reply")
        await update.message.reply_text(f"Sorry, I could not generate a reply right now: {exc}")
        return
    for part in split_message(reply):
        await update.message.reply_text(part)

# --- Run bot in background thread ---
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

# --- Streamlit UI ---
st.title("Retail Radar Telegram Bot")

if st.button("Start Telegram Bot"):
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("Telegram bot started in background thread ✅")
