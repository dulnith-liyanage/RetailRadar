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

dataset_string = df.head(5).to_string()

describe = df.describe().to_markdown(index=True)
correlation = df.corr(numeric_only=True).to_markdown(index=True)

year_data = df.groupby("Year")["Total_Price_LKR"].sum().reset_index()
year_data["Total_Price_LKR"] = year_data["Total_Price_LKR"] / 1000000
year_data_md = year_data.to_markdown(index=False)

monthly_revenue = df.groupby(["Year", "Month"])["Total_Price_LKR"].sum().reset_index()
monthly_revenue["Total_Price_LKR"] = monthly_revenue["Total_Price_LKR"] / 1000000
monthly_revenue["Year"] = monthly_revenue["Year"].astype(str)
monthly_revenue_md = monthly_revenue.to_markdown(index=False)

districtwise_data = df.groupby(["District"])["Total_Price_LKR"].sum().reset_index()
districtwise_data["Total_Price_LKR"] = districtwise_data["Total_Price_LKR"] / 100000
districtwise_data_md = districtwise_data.to_markdown(index=False)

product_revenue = df.groupby("Description")["Total_Price_LKR"].sum().sort_values(ascending=False).reset_index()
product_revenue["Total_Price_LKR"] = product_revenue["Total_Price_LKR"] / 1000000
top_products_by_revenue_md = product_revenue.head(10).to_markdown(index=False)
bottom_products_by_revenue_md = product_revenue.tail(5).sort_values("Total_Price_LKR").to_markdown(index=False)

product_quantity = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).reset_index()
top_products_by_quantity_md = product_quantity.head(10).to_markdown(index=False)

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekly_sales = df.groupby("Day")["Total_Price_LKR"].sum().reset_index()
weekly_sales["Total_Price_LKR"] = weekly_sales["Total_Price_LKR"] / 1000000
weekly_sales["Day"] = pd.Categorical(weekly_sales["Day"], categories=day_order, ordered=True)
weekly_sales = weekly_sales.sort_values("Day")
weekly_sales_md = weekly_sales.to_markdown(index=False)

hourly_sales = df.groupby("Hour")["Total_Price_LKR"].sum().reset_index()
hourly_sales["Total_Price_LKR"] = hourly_sales["Total_Price_LKR"] / 1000000
hourly_sales_md = hourly_sales.to_markdown(index=False)

customers, cluster_counts, segment_summary_md, _ = get_segment_summary(df)
total_customers = customers["CustomerID"].nunique()

# --- Sales Forecast (shared with the Streamlit app's Forecast tab and bot.py) ---
history_recent, forecast_dataset, forecast_combined, forecast_summary_md, forecast_peak_period, forecast_model = \
    get_sales_forecast(df, is_uploaded=False)

avg_recent_actual = history_recent["Sales"].mean()
avg_forecast = forecast_dataset["Sales"].mean()
forecast_trend = "upward" if avg_forecast > avg_recent_actual else "downward"
forecast_trend_pct = abs((avg_forecast - avg_recent_actual) / avg_recent_actual) * 100 if avg_recent_actual else 0
forecast_prev_year_label = history_recent["Year_Label"].iloc[0]
forecast_year_label = forecast_dataset["Year_Label"].iloc[0]


def get_revenue_data():
    return f"[YEARLY REVENUE]\n{year_data_md}\n[MONTHLY REVENUE]\n{monthly_revenue_md}\n[DISTRICT REVENUE]\n{districtwise_data_md}"

def get_product_data():
    return f"[TOP PRODUCTS BY REVENUE]\n{top_products_by_revenue_md}\n[TOP PRODUCTS BY QUANTITY]\n{top_products_by_quantity_md}\n[BOTTOM PRODUCTS]\n{bottom_products_by_revenue_md}"

def get_segment_data():
    return f"[CUSTOMER SEGMENTS]\n{segment_summary_md}"

def get_forecast_data():
    return f"[SALES FORECAST]\n{forecast_summary_md}"

def get_timing_data():
    return f"[WEEKLY SALES]\n{weekly_sales_md}\n[HOURLY SALES]\n{hourly_sales_md}"

available_tools = {
    "get_revenue_data": get_revenue_data,
    "get_product_data": get_product_data,
    "get_segment_data": get_segment_data,
    "get_forecast_data": get_forecast_data,
    "get_timing_data": get_timing_data,
}

tools = [
    {"type": "function", "function": {"name": "get_revenue_data", "description": "Get yearly, monthly, and district revenue."}},
    {"type": "function", "function": {"name": "get_product_data", "description": "Get top and bottom performing products."}},
    {"type": "function", "function": {"name": "get_segment_data", "description": "Get customer segments, RFM, and K-Means data."}},
    {"type": "function", "function": {"name": "get_forecast_data", "description": "Get the next 12 months sales forecast."}},
    {"type": "function", "function": {"name": "get_timing_data", "description": "Get revenue trends by day of week and hour of day."}}
]

def build_system_prompt() -> str:
    return f"""You are 'Insight.AI', the specialized chatbot for 'Retail Radar'.
You have tools to fetch specific data matrices. Always call the appropriate tool when a user asks for data you don't have in context.
Keep answers concise, direct, and factual.
[DESCRIPTIVE STATISTICS]:\n{describe}\n[CORRELATION MATRIX]:\n{correlation}"""

SYSTEM_PROMPT = build_system_prompt()



def generate_reply(prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            if func_name in available_tools:
                func_response = available_tools[func_name]()
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": func_response,
                })
        # Second call to get final answer
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        msg = response.choices[0].message
    return msg.content or "I could not generate a response."

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
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True, stop_signals=())

# --- Streamlit UI ---
st.title("Retail Radar Telegram Bot")

if st.button("Start Telegram Bot"):
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("Telegram bot started in background thread ✅")
