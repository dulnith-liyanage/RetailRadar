import pandas as pd
from utils import get_raw_data, clean_data
import streamlit as st

row_df, is_uploade = get_raw_data()

df = clean_data(row_df)

describe = df.describe().to_markdown(index=True)
correlation = df.corr(numeric_only = True).to_markdown()
print(correlation)