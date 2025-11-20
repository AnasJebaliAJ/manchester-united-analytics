import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Manchester United Analytics Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("combined_seasons.csv")

df = load_data()
st.write("### Dataset Preview")
st.dataframe(df.head())

# Your charts here...
