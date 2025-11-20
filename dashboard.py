import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("⚽ Manchester United Analytics Dashboard (Interactive)")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("combined_seasons.csv")

df = load_data()

# Filter MU matches only
df["is_mu_match"] = df.apply(
    lambda row: (
        row["home_team"] == "Man United" or row["away_team"] == "Man United"
    ),
    axis=1
)

mu_matches = df[df["is_mu_match"]].copy()

# Determine MU win/loss/draw
def mu_result(row):
    if row["home_team"] == "Man United":
        if row["home_goals"] > row["away_goals"]:
            return "W"
        elif row["home_goals"] < row["away_goals"]:
            return "L"
        else:
            return "D"
    else:
        if row["away_goals"] > row["home_goals"]:
            return "W"
        elif row["away_goals"] < row["home_goals"]:
            return "L"
        else:
            return "D"

mu_matches["mu_result"] = mu_matches.apply(mu_result, axis=1)

# Sidebar filters
st.sidebar.title("Filters")

seasons = st.sidebar.multiselect(
    "Select Season(s):", 
    sorted(df["Season"].unique()), 
    default=sorted(df["Season"].unique())
)

referees = st.sidebar.multiselect(
    "Select Referee(s):", 
    sorted(mu_matches["Referee"].unique()),
    default=sorted(mu_matches["Referee"].unique())
)

filtered = mu_matches[
    (mu_matches["Season"].isin(seasons)) &
    (mu_matches["Referee"].isin(referees))
].copy()

# Referee match count
filtered["match_count"] = filtered["Referee"].map(filtered["Referee"].value_counts())

# Win rate per Referee
win_rate_ref = (
    filtered.groupby("Referee")["mu_result"]
            .apply(lambda x: (x == "W").mean() * 100)
            .sort_values(ascending=False)
)

# Goal difference per Referee
filtered["goal_diff"] = filtered.apply(
    lambda row: (row["home_goals"] - row["away_goals"]) if row["home_team"] == "Man United"
                else (row["away_goals"] - row["home_goals"]),
    axis=1
)

gd_ref = filtered.groupby("Referee")["goal_diff"].mean().sort_values()

# Win rate per season
win_rate_season = (
    filtered.groupby("Season")["mu_result"]
            .apply(lambda x: (x == "W").mean() * 100)
)

# Heatmap matrix
heatmap_data = (
    filtered.groupby(["Referee", "Season"])["mu_result"]
            .apply(lambda x: (x == "W").mean() * 100)
            .unstack(fill_value=0)
)


# ======================================
# LAYOUT
# ======================================

st.subheader("🔵 Win % by Referee (Interactive Bar Chart)")
fig1 = px.bar(
    win_rate_ref,
    x=win_rate_ref.values,
    y=win_rate_ref.index,
    orientation="h",
    color=win_rate_ref.values,
    color_continuous_scale="reds",
    labels={"x": "Win %", "y": "Referee"},
    title="MU Win % by Referee"
)
st.plotly_chart(fig1, use_container_width=True)


st.subheader("🔴 Average Goal Difference by Referee")
fig2 = px.bar(
    gd_ref,
    x=gd_ref.values,
    y=gd_ref.index,
    orientation="h",
    color=gd_ref.values,
    color_continuous_scale="RdBu",
    title="Goal Difference by Referee"
)
st.plotly_chart(fig2, use_container_width=True)


st.subheader("🟢 Win % by Season (Trend Chart)")
fig3 = px.line(
    win_rate_season,
    markers=True,
    labels={"value": "Win %", "index": "Season"},
    title="MU Win % per Season"
)
st.plotly_chart(fig3, use_container_width=True)


st.subheader("🟣 Win % Heatmap (Referee × Season)")
fig4 = px.imshow(
    heatmap_data,
    color_continuous_scale="Blues",
    text_auto=".1f",
    labels={"x": "Season", "y": "Referee", "color": "Win %"},
    title="MU Win % by Referee per Season"
)
st.plotly_chart(fig4, use_container_width=True)


# Match count summary
st.subheader("📊 Referee Match Counts (Filtered)")
st.dataframe(
    filtered.groupby("Referee")["match_count"].first().sort_values(ascending=False)
)
