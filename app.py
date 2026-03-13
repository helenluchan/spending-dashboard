import streamlit as st
import pandas as pd
import plotly.express as px

def render_table(df):
    html = df.to_html(classes="custom-table", border=0)
    st.markdown(html, unsafe_allow_html=True)

st.set_page_config(page_title="Helen's Spend Dashboard", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #0f0f0f; color: #f5f5f5; }
    .block-container { padding-top: 0.5rem !important; }
    #MainMenu, footer, header { visibility: hidden; }

    h1 { color: #ffffff !important; font-weight: 700 !important; font-size: 2rem !important; letter-spacing: -0.5px; }
    h2, h3 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.1rem !important; }

    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 10px 14px;
    }
    [data-testid="stMetricLabel"] p { color: #9ca3af !important; font-size: 0.7rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.2rem !important; font-weight: 700 !important; }
    [data-testid="stSelectbox"] label { color: #ffffff !important; font-size: 0.75rem !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] { font-size: 0.8rem !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div { min-height: 32px !important; padding: 2px 8px !important; background-color: #1a1a1a !important; border-color: #2a2a2a !important; color: #ffffff !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] span { color: #ffffff !important; }

    hr { border-color: #2a2a2a !important; margin: 1.5rem 0 !important; }

    .stTable table { background-color: #1a1a1a !important; border-radius: 12px; overflow: hidden; }
    .stTable th { background-color: #222222 !important; color: #9ca3af !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #2a2a2a !important; font-weight: 500 !important; }
    .stTable td { color: #e5e7eb !important; border-bottom: 1px solid #1f1f1f !important; font-size: 0.95rem !important; }
    .stTable tr:hover td { background-color: #222222 !important; }
    table.custom-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    table.custom-table th { color: #6b7280; padding: 6px 12px; text-align: left; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #2a2a2a; font-weight: 500; }
    table.custom-table td { color: #ffffff; padding: 8px 12px; border-bottom: 1px solid #1f1f1f; }
    table.custom-table tr:last-child td { border-bottom: none; }
    table.custom-table tr:hover td { background-color: #1a1a1a; }
    [data-testid="stExpander"] { background-color: #1a1a1a !important; border: 1px solid #2a2a2a !important; border-radius: 8px !important; }
    [data-testid="stExpander"] summary p { color: #ffffff !important; }
    [data-testid="stExpander"] summary:hover p { color: #00d37f !important; }
    [data-testid="stExpander"] summary span { color: transparent !important; font-size: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- Load & clean data ---
CSV_URL = "https://gist.githubusercontent.com/helenluchan/0d0370b7bfa754c809d75217739f8842/raw/bc1718a558f36e18f8f0175d21ba59518b8f5010/helen%2520spend%2520data_30%2520days_march%252012"
df = pd.read_csv(CSV_URL, sep="\t")
df.columns = df.columns.str.strip()
df["Transaction Date"] = pd.to_datetime(df["Transaction Date"])
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df[df["Type"] == "Sale"].copy()
df["Amount"] = df["Amount"].abs()


# Recategorize subscriptions
df.loc[df["Description"].str.contains("OPENAI|YouTubePremium", case=False, na=False), "Category"] = "Subscriptions"
df.loc[df["Category"] == "Groceries", "Category"] = "Food & Drink"
df.loc[df["Description"].str.contains("DELI", case=False, na=False), "Category"] = "Food & Drink"

df["Month"] = df["Transaction Date"].dt.to_period("M").astype(str)

# --- Constants ---
COLORS = ["#00d37f", "#4FC3F7", "#a78bfa", "#fb923c", "#f472b6", "#fbbf24", "#34d399", "#60a5fa"]
CHART_LAYOUT = dict(
    paper_bgcolor="#1a1a1a",
    plot_bgcolor="#1a1a1a",
    font=dict(family="Inter", color="#9ca3af", size=14),
    title_font=dict(family="Inter", color="#ffffff", size=18, weight=600),
    legend=dict(bgcolor="#1a1a1a", bordercolor="#2a2a2a", borderwidth=1, font=dict(color="#9ca3af", size=13)),
    margin=dict(t=50, b=20, l=20, r=20),
)

# --- Header ---
end_date = df["Transaction Date"].max()
end_dt = end_date
start_date = (end_dt - pd.Timedelta(days=29)).strftime("%b %-d")
end_date = end_dt.strftime("%b %-d, %Y")
st.title("Helen's Spend Dashboard")
st.markdown(f"<p style='color:#9ca3af; font-size:0.95rem; margin-top:-12px;'>{start_date} — {end_date}</p>", unsafe_allow_html=True)

# --- Top metrics ---
total = df["Amount"].sum()
by_cat = df.groupby("Category")["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
top_cat = by_cat.iloc[0]["Category"]
avg_daily = df.groupby("Transaction Date")["Amount"].sum().mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Spent", f"${total:,.2f}")
c2.metric("🧾 Transactions", len(df))
c3.metric("📅 Avg Daily Spend", f"${avg_daily:,.2f}")
c4.metric("🏆 Top Category", top_cat)

st.divider()

# --- Charts ---
col_left, col_right = st.columns(2)

# Daily spend line
ANNOTATIONS = {
    "2026-02-15": "Landed at JFK. Got a donut immediately.",
    "2026-02-18": "Celebrated CNY with family. Grandma wanted pizza and Popeyes.",
    "2026-03-10": "Stayed inside to apply to jobs. Just got a coffee.",
    "2026-03-01": "Travel day. Booked a shuttle. And my gym charged me too.",
    "2026-03-11": "Bought Claude AI subscription.",
}
daily = df.groupby("Transaction Date")["Amount"].sum().reset_index()
daily["Note"] = daily["Transaction Date"].dt.strftime("%Y-%m-%d").map(ANNOTATIONS).fillna("")
fig_line = px.line(
    daily, x="Transaction Date", y="Amount",
    title="Daily Spend",
    labels={"Amount": "Amount ($)", "Transaction Date": ""},
    color_discrete_sequence=["#00d37f"],
)
fig_line.update_traces(
    line=dict(width=2), mode="lines+markers",
    marker=dict(size=6, color="#00d37f"),
    customdata=daily["Note"],
    hovertemplate="<b>%{x|%b %d}</b><br>$%{y:,.2f}<br>%{customdata}<extra></extra>",
)
fig_line.update_layout(
    xaxis=dict(tickfont=dict(color="#9ca3af"), gridcolor="#2a2a2a", tickformat="%b %d"),
    yaxis=dict(tickfont=dict(color="#9ca3af"), gridcolor="#2a2a2a", tickprefix="$"),
    **CHART_LAYOUT,
)
selected = col_left.plotly_chart(fig_line, use_container_width=True, on_select="rerun", selection_mode="points")

if selected and selected.get("selection", {}).get("points"):
    point = selected["selection"]["points"][0]
    clicked_date = pd.to_datetime(point["x"]).strftime("%m/%d/%Y")
    day_df = df[df["Transaction Date"].dt.strftime("%m/%d/%Y") == clicked_date][["Description", "Category", "Amount"]].copy()
    day_df["Amount"] = day_df["Amount"].map("${:,.2f}".format)
    day_df = day_df.reset_index(drop=True)
    day_df.index += 1
    col_left.markdown(f"**Transactions on {clicked_date}**")
    col_left.markdown(day_df.to_html(classes="custom-table", border=0), unsafe_allow_html=True)

# Category pie
tx_counts = df.groupby("Category").size().reset_index(name="Count")
by_cat = by_cat.merge(tx_counts, on="Category", how="left")

fig_pie = px.pie(
    by_cat, names="Category", values="Amount",
    title="Category Spend", hole=0.55,
    color_discrete_sequence=COLORS,
)
fig_pie.update_traces(
    textfont=dict(color="#ffffff", size=12),
    marker=dict(line=dict(color="#1a1a1a", width=2)),
    customdata=by_cat[["Count"]].values,
    hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<br>%{customdata[0]} transactions<extra></extra>",
)
fig_pie.update_layout(**CHART_LAYOUT)
col_right.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --- Fun facts ---
mta_rides = len(df[df["Description"].str.contains("MTA", case=False, na=False)])
path_rides = len(df[df["Description"] == "PATH"])

all_dates = pd.date_range(df["Transaction Date"].min(), df["Transaction Date"].max())
spend_dates = set(df["Transaction Date"].dt.date)
no_spend_streak = current_streak = 0
for d in all_dates:
    if d.date() not in spend_dates:
        current_streak += 1
        no_spend_streak = max(no_spend_streak, current_streak)
    else:
        current_streak = 0

biggest = df.loc[df["Amount"].idxmax()]

st.subheader("✨ Fun Facts")
ff1, ff2, ff3 = st.columns(3)
ff1.metric("🚇 MTA Rides", mta_rides)
ff2.metric("🧘🏽 No-Spend Streak", f"{no_spend_streak} days")
ff3.metric("💥 Biggest Splurge", f"{biggest['Description']} · ${biggest['Amount']:,.2f} · {biggest['Transaction Date'].strftime('%b %d')}")

st.divider()

# --- Top 10 transactions ---
st.subheader("Top 10 Transactions $$$")
top10 = df.nlargest(10, "Amount")[["Transaction Date", "Description", "Category", "Amount"]].reset_index(drop=True)
top10["Transaction Date"] = top10["Transaction Date"].dt.strftime("%b %-d, %Y")
top10["Amount"] = top10["Amount"].map("${:,.2f}".format)
top10.index += 1
top10 = top10.rename(columns={"Description": "Merchant", "Transaction Date": "Date"})
render_table(top10)

# --- All transactions ---
categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())

with st.expander("All Transactions", expanded=False):
    selected_cat = st.selectbox("Filter by Category", categories)

    all_tx = df[["Transaction Date", "Description", "Category", "Amount"]].sort_values("Transaction Date", ascending=False).copy()
    if selected_cat != "All":
        all_tx = all_tx[all_tx["Category"] == selected_cat]
    filtered_total = all_tx["Amount"].sum()

    all_tx = all_tx.reset_index(drop=True)
    all_tx["Transaction Date"] = all_tx["Transaction Date"].dt.strftime("%b %-d, %Y")
    all_tx["Amount"] = all_tx["Amount"].map("${:,.2f}".format)
    all_tx = all_tx.rename(columns={"Description": "Merchant", "Transaction Date": "Date"})
    all_tx.index += 1
    render_table(all_tx)
    st.markdown(f"<p style='text-align:right; color:#00d37f; font-weight:600; font-size:0.9rem; margin-top:4px;'>Total: ${filtered_total:,.2f}</p>", unsafe_allow_html=True)

st.divider()
st.markdown("👀 Want to see more? I take suggestions at [linkedin.com/in/helenluchan](https://www.linkedin.com/in/helenluchan/)", unsafe_allow_html=True)

st.divider()
st.markdown("""
<p style='color:#6b7280; font-size:0.8rem; line-height:1.7;'>
  <span style='color:#ffffff; font-weight:600;'>How I built this</span><br>
  Built with <strong style='color:#d1d5db;'>Python</strong> and <strong style='color:#d1d5db;'>Streamlit</strong> for the web framework,
  <strong style='color:#d1d5db;'>pandas</strong> for data processing, and <strong style='color:#d1d5db;'>Plotly</strong> for interactive charts.
  Transaction data is exported from my recent credit card statement and hosted as a CSV on a secret <strong style='color:#d1d5db;'>GitHub Gist</strong> —
  the dashboard fetches it live on every load. Deployed on <strong style='color:#d1d5db;'>Streamlit Community Cloud</strong>.
  Vibe-coded with <strong style='color:#d1d5db;'>Claude</strong>. Design, debugging, and way too many food purchases — all mine.
</p>
""", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280; font-size:0.8rem;'>Not optimized for mobile (yet). Check me out on a desktop.</p>", unsafe_allow_html=True)
