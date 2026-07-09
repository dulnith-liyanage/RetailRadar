import pandas as pd
import numpy as np
import yfinance as yf

def get_yfinance_exchange_rate(base_currency, target_currency):
    ticker_string = f"{base_currency}{target_currency}=X"
    
    ticker = yf.Ticker(ticker_string)
    
    # Get the latest day's market data
    todays_data = ticker.history(period='1d')
    
    # Extract the closing price
    current_rate = todays_data['Close'].iloc[0]
    
    return current_rate

live_rate = get_yfinance_exchange_rate("USD", "LKR")
print(f"Current USD to LKR rate: Rs. {live_rate:.2f}")

print("Loading the Online Retail dataset...")


# --- 1. LOAD DATA AND CLEAN ---

try:
    df = pd.read_csv('online_retail.csv', encoding='ISO-8859-1')
except FileNotFoundError:
    print("Error: 'online_retail.csv' not found. Please ensure it is in the same directory.")
    exit()

print("Cleaning data...")

# Drop rows where CustomerID is missing
df.dropna(subset=['CustomerID'], inplace=True)

# Remove cancelled orders and negative quantities
df = df[df['Quantity'] > 0]

# Convert CustomerID to integer for cleaner data
df['CustomerID'] = df['CustomerID'].astype(int)

# --- 2. DROP COUNTRY COLUMN ---
print("Dropping 'Country' column...")
if 'Country' in df.columns:
    df.drop(columns=['Country'], inplace=True)


# --- 3. CURRENCY LOCALIZATION (USD to LKR) ---
print("Converting pricing to Sri Lankan Rupees (LKR)...")
# Using the live exchange rate for more accurate localization
exchange_rate = live_rate
df['UnitPrice_LKR'] = df['UnitPrice'] * exchange_rate

# Calculate the total value of each line item
df['Total_Price_LKR'] = df['Quantity'] * df['UnitPrice_LKR']


# --- 4. GEOGRAPHIC LOCALIZATION ---
print("Assigning Sri Lankan districts to customers...")
# Define target districts. We use weights to simulate a realistic urban commercial density
# Define all 25 districts of Sri Lanka
districts = [
    'Colombo', 'Gampaha', 'Kandy', 'Kurunegala', 'Kalutara', 'Galle', 
    'Ratnapura', 'Kegalle', 'Matara', 'Badulla', 'Anuradhapura', 
    'Jaffna', 'Puttalam', 'Ampara', 'Batticaloa', 'Nuwara Eliya', 
    'Matale', 'Hambantota', 'Trincomalee', 'Polonnaruwa', 'Monaragala', 
    'Vavuniya', 'Mannar', 'Kilinochchi', 'Mullaitivu'
]

# Weights simulating realistic urban commercial/population density (Must sum to 1.0)
weights = [
    0.26,  # Colombo (Highest commercial density)
    0.15,  # Gampaha
    0.08,  # Kandy
    0.07,  # Kurunegala
    0.06,  # Kalutara
    0.05,  # Galle
    0.04,  # Ratnapura
    0.03,  # Kegalle
    0.03,  # Matara
    0.03,  # Badulla
    0.03,  # Anuradhapura
    0.02,  # Jaffna
    0.02,  # Puttalam
    0.02,  # Ampara
    0.02,  # Batticaloa
    0.02,  # Nuwara Eliya
    0.01,  # Matale
    0.01,  # Hambantota
    0.01,  # Trincomalee
    0.01,  # Polonnaruwa
    0.01,  # Monaragala
    0.005, # Vavuniya
    0.005, # Mannar
    0.005, # Kilinochchi
    0.005  # Mullaitivu
]

unique_customers = df['CustomerID'].unique()
np.random.seed(42) # Set seed so the random assignment is identical every time you run it

# Generate a list of districts based on the defined probabilities
assigned_districts = np.random.choice(districts, size=len(unique_customers), p=weights)

# This ensures that a single CustomerID always has the same district across all their purchases
customer_district_map = dict(zip(unique_customers, assigned_districts))
df['District'] = df['CustomerID'].map(customer_district_map)

# --- 5. EXPORT ---
output_filename = 'online_retail_lk.csv'
print(f"Saving localized dataset to '{output_filename}'...")
df.to_csv(output_filename, index=False)

print("Pipeline complete! Your dataset is fully Sri Lankanized and ready for K-Means clustering.")