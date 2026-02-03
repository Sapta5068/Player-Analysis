import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Sanju Samson – T20I Selection Analysis",
    layout="wide"
)

st.title("Sanju Samson – T20I Playing XI Selection Analysis")
st.caption("Interactive selector-style performance analysis")

@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\USER\Documents\Folder2\Match Analysis.csv")
    df['Match_Date'] = pd.to_datetime(df['Match_Date'], format="%d-%m-%Y")
    df = df.sort_values('Match_Date').reset_index(drop=True)
    return df

df = load_data()

df['Batting_Impact'] = df['Runs'] * (df['Strike_Rate'] / 100)
df['Fielding_Impact'] = (df['Catches'] * 10) + (df['Stumpings'] * 15)
df['Total_Impact'] = df['Batting_Impact'] + df['Fielding_Impact']
df['Dismissals'] = df['Catches'] + df['Stumpings']

st.sidebar.header("🔎 Filters")

role_filter = st.sidebar.radio(
    "Select Role",
    ["All", "Wicket-Keeper", "Batsman"]
)

start_date, end_date = st.sidebar.date_input(
    "Match Date Range",
    [df['Match_Date'].min(), df['Match_Date'].max()]
)

rolling_window = st.sidebar.slider(
    "Momentum Window (matches)",
    3, 10, 5
)

filtered_df = df[
    (df['Match_Date'] >= pd.to_datetime(start_date)) &
    (df['Match_Date'] <= pd.to_datetime(end_date))
]

if role_filter != "All":
    filtered_df = filtered_df[filtered_df['Role'] == role_filter]

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Matches", len(filtered_df))
col2.metric("Avg Runs", round(filtered_df['Runs'].mean(), 2))
col3.metric("Avg Strike Rate", round(filtered_df['Strike_Rate'].mean(), 2))
col4.metric("Consistency % (20+)", round((filtered_df['Runs'] >= 20).mean()*100, 1))
col5.metric("Avg Fielding Impact", round(filtered_df['Fielding_Impact'].mean(), 2))

filtered_df['Rolling_Impact'] = (
    filtered_df['Total_Impact'].rolling(rolling_window).mean()
)

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(filtered_df['Match_Date'], filtered_df['Rolling_Impact'], marker='o')
ax.set_title(f"{rolling_window}-Match Rolling Impact")
ax.set_xlabel("Match Date")
ax.set_ylabel("Impact Score")
st.pyplot(fig)

st.subheader("🏏 Batting Performance")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    ax.plot(filtered_df['Match_Date'], filtered_df['Runs'], marker='o')
    ax.set_title("Runs per Match")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    ax.plot(filtered_df['Match_Date'], filtered_df['Strike_Rate'], marker='o', color='orange')
    ax.set_title("Strike Rate Trend")
    st.pyplot(fig)

st.subheader("🧤 Fielding Contribution")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    ax.bar(filtered_df['Match_Date'], filtered_df['Dismissals'])
    ax.set_title("Dismissals per Match")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    ax.pie(
        [filtered_df['Batting_Impact'].sum(),
         filtered_df['Fielding_Impact'].sum()],
        labels=["Batting", "Fielding"],
        autopct="%1.1f%%"
    )
    ax.set_title("Batting vs Fielding Impact")
    st.pyplot(fig)

st.subheader("🔁 Role-Based Impact Comparison")

role_summary = (
    df.groupby('Role')
      .agg(
          Matches=('Match_ID','count'),
          Avg_Runs=('Runs','mean'),
          Avg_SR=('Strike_Rate','mean'),
          Avg_Total_Impact=('Total_Impact','mean'),
          Avg_Fielding_Impact=('Fielding_Impact','mean')
      )
      .round(2)
)

st.dataframe(role_summary)

st.subheader("✅ Selection Verdict")

avg_sr = filtered_df['Strike_Rate'].mean()
consistency = (filtered_df['Runs'] >= 20).mean() * 100
avg_fielding = filtered_df['Fielding_Impact'].mean()

if avg_sr >= 140 and consistency >= 50 and avg_fielding >= 10:
    st.success("✔ Strong Playing XI Candidate – Wicket-Keeper Batter")
elif avg_sr >= 130:
    st.warning("⚠ Conditional Selection – Role dependent")
else:
    st.error("❌ Not ideal for current Playing XI")

st.subheader("📋 Match-by-Match Explorer")
st.dataframe(filtered_df.reset_index(drop=True))
