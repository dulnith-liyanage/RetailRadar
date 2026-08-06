#!.venv/bin/python

import logging
import os
from functools import lru_cache
import pandas as pd
from groq import Groq
from telegram import Update
import streamlit as st
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from utils import clean_data, get_raw_data, get_segment_summary


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GROQ_API_KEY = st.secrets['API_KEY']
TELEGRAM_BOT_TOKEN = st.secrets['TELE_BOT_API']
if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ API key. Set the API_KEY environment variable.")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Missing Telegram bot token. Set the TELE_BOT_API environment variable.")

client = Groq(api_key=GROQ_API_KEY)

raw_df, _ = get_raw_data()
df = clean_data(raw_df)
dataset_string = df.head(100).to_string()

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
top_products_by_revenue_md = product_revenue.head(15).to_markdown(index=False)
bottom_products_by_revenue_md = product_revenue.tail(10).sort_values("Total_Price_LKR").to_markdown(index=False)

product_quantity = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).reset_index()
top_products_by_quantity_md = product_quantity.head(15).to_markdown(index=False)

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekly_sales = df.groupby("Day")["Total_Price_LKR"].sum().reset_index()
weekly_sales["Total_Price_LKR"] = weekly_sales["Total_Price_LKR"] / 1000000
weekly_sales["Day"] = pd.Categorical(weekly_sales["Day"], categories=day_order, ordered=True)
weekly_sales = weekly_sales.sort_values("Day")
weekly_sales_md = weekly_sales.to_markdown(index=False)

hourly_sales = df.groupby("Hour")["Total_Price_LKR"].sum().reset_index()
hourly_sales["Total_Price_LKR"] = hourly_sales["Total_Price_LKR"] / 1000000
hourly_sales_md = hourly_sales.to_markdown(index=False)

customers, _, segment_summary_md = get_segment_summary(df)
total_customers = customers["CustomerID"].nunique()


def build_system_prompt() -> str:
    return f"""You are 'Insight.AI', the specialized chatbot for 'Retail Radar' analytical platform.
Your job is to deliver concise data insights based on the matrices provided below.
All revenue metrics are customized for Sri Lankan Rupees (LKR).

[DATASET SAMPLE]:
{dataset_string}

[DESCRIPTIVE STATISTICS]:
{describe}

[CORRELATION MATRIX]:
{correlation}

[YEARLY REVENUE (In Millions LKR)]:
{year_data_md}

[MONTHLY REVENUE BREAKDOWN (In Millions LKR)]:
{monthly_revenue_md}

[DISTRICT-WISE REVENUE PERFORMANCE (In Lakhs/100k LKR)]:
{districtwise_data_md}

[TOP 15 PRODUCTS BY REVENUE (In Millions LKR)]:
{top_products_by_revenue_md}

[TOP 15 PRODUCTS BY SOLD QUANTITY (Units)]:
{top_products_by_quantity_md}

[BOTTOM 10 PRODUCTS BY REVENUE (In Millions LKR)]:
{bottom_products_by_revenue_md}

[DAY-OF-WEEK REVENUE TREND (In Millions LKR)]:
{weekly_sales_md}

[HOURLY REVENUE TREND (In Millions LKR)]:
{hourly_sales_md}

[CUSTOMER SEGMENTATION OVERVIEW]:
Total unique customers: {total_customers}
Customers are grouped via RFM (Recency, Frequency, Monetary) analysis and K-Means clustering
into behavioral segments. Segment name, customer count, and average spend per customer
(in thousand LKR) are shown below:
{segment_summary_md}

Rules: Keep answers business-oriented, direct, and factual. Always clarify whether monetary
values are displayed in Millions, Lakhs, or Thousands based on the data keys above. When asked
about customers, loyalty, churn risk, or segments, use the CUSTOMER SEGMENTATION OVERVIEW table
rather than guessing. When asked about timing, footfall, staffing, or "best time to shop/promote",
use the DAY-OF-WEEK and HOURLY REVENUE TREND tables. When asked about products, bestsellers,
top sellers, or worst/weakest performers, use the TOP/BOTTOM PRODUCTS BY REVENUE and TOP PRODUCTS
BY SOLD QUANTITY tables rather than guessing.

Answer format: Before answering a "best/worst/highest/lowest/top" question, scan the full
relevant table yourself and identify the single row with the correct max or min value silently.
State only that final answer as your opening sentence, with its exact figure. Keep answers to
1-3 sentences unless the user asks for more detail or a breakdown."""


def generate_reply(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or "I could not generate a response."


def split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
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

    logging.info(
        "Received Telegram message from %s: %s",
        update.effective_user.id if update.effective_user else "unknown",
        prompt,
    )

    try:
        reply = generate_reply(prompt)
    except Exception as exc:
        logging.exception("Failed to generate Telegram reply")
        await update.message.reply_text(f"Sorry, I could not generate a reply right now: {exc}")
        return

    for part in split_message(reply):
        await update.message.reply_text(part)


def main() -> None:
    print("Starting Telegram bot... Press Ctrl+C to stop.")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
