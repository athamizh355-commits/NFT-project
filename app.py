"""
NFT Market Analytics Dashboard
================================
Enhanced Streamlit dashboard that mirrors the HTML design:
  - Dark theme (#0f0f1a background, #1a1a2e cards)
  - Collection colour palette matching the HTML
  - All 6 sections: Sales & Revenue, Market Trends, Event Analysis,
    Price Analysis, Volume Analysis, Top 10 Rankings
  - Metric cards, Plotly charts with matching dark style, styled tables

Usage
-----
    pip install streamlit plotly pandas
    streamlit run nft_dashboard.py

The script ships with the same hard-coded sample data that powers the HTML
dashboard.  Replace the load_data() function with real CSV reads to use
your own CSVs.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NFT Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Colour palette (mirrors the HTML) ─────────────────────────────────────────
COLLS   = ["CryptoPunks", "BAYC", "MAYC", "Doodles", "Pudgy Penguins"]
CKEYS   = ["#534AB7", "#1D9E75", "#D85A30", "#BA7517", "#D4537E"]
CMAP    = dict(zip(COLLS, CKEYS))
BG      = "#0f0f1a"
CARD_BG = "#1a1a2e"
BORDER  = "#2a2a3e"
TICK    = "#666666"
GRID    = "rgba(255,255,255,0.07)"
TEXT    = "#e0e0e0"
SUBTEXT = "#999999"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── App background ─────────────────── */
  [data-testid="stAppViewContainer"],
  [data-testid="stHeader"],
  section.main > div {{
    background: {BG} !important;
  }}
  [data-testid="stSidebar"] {{ background: #12121f !important; }}

  /* ── Remove default top padding ─────── */
  .block-container {{ padding-top: 3.5rem !important; }}

  /* ── Tab strip ──────────────────────── */
  [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 6px;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 0;
  }}
  [data-baseweb="tab"] {{
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px 8px 0 0 !important;
    color: {SUBTEXT} !important;
    font-size: 13px !important;
    padding: 7px 18px !important;
    transition: all 0.15s;
  }}
  [aria-selected="true"][data-baseweb="tab"] {{
    background: #534AB7 !important;
    border-color: #534AB7 !important;
    color: white !important;
  }}
  [data-baseweb="tab-highlight"] {{ display: none !important; }}
  [data-baseweb="tab-panel"] {{ background: transparent !important; padding-top: 1rem; }}

  /* ── Metric card ─────────────────────── */
  .metric-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-bottom: 0;
  }}
  .metric-label {{
    font-size: 11px;
    color: {SUBTEXT};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
  }}
  .metric-value {{
    font-size: 26px;
    font-weight: 500;
    color: #f0f0f0;
    line-height: 1.1;
  }}
  .metric-unit {{
    font-size: 11px;
    color: #666;
    margin-top: 3px;
  }}

  /* ── Chart card ─────────────────────── */
  .chart-title {{
    font-size: 13px;
    font-weight: 500;
    color: #cccccc;
    margin-bottom: 6px;
    padding: 1rem 1.25rem 0;
  }}

  /* ── Plotly iframe background ────────── */
  .js-plotly-plot .plotly {{ background: transparent !important; }}

  /* ── Styled data table ───────────────── */
  .styled-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    color: {TEXT};
  }}
  .styled-table th {{
    font-size: 11px;
    font-weight: 500;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 6px 8px;
    border-bottom: 1px solid {BORDER};
    text-align: left;
  }}
  .styled-table td {{
    padding: 7px 8px;
    border-bottom: 1px solid #1e1e30;
    color: #cccccc;
  }}
  .styled-table tr:last-child td {{ border-bottom: none; }}
  .rank {{ font-weight: 500; color: #666; }}
  .coll-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
  }}
  .num-right {{ text-align: right; font-weight: 500; color: #f0f0f0; }}
  .num-right-dim {{ text-align: right; color: #aaa; }}

  /* ── Card wrapper ────────────────────── */
  .card-wrap {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.1rem 0 1rem;
    margin-bottom: 1rem;
  }}

  /* ── Header ──────────────────────────── */
  .dash-header {{
    display: flex; align-items: center; gap: 14px; margin-bottom: 1.25rem;
  }}
  .dash-logo {{
    width: 40px; height: 40px; border-radius: 10px;
    background: #534AB7;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 20px;
  }}
  .dash-title {{ font-size: 22px; font-weight: 500; color: #f0f0f0; }}
  .dash-sub   {{ font-size: 13px; color: #888; margin-top: 3px; }}

  /* General text colour override */
  p, span, div, h1, h2, h3, h4, label {{ color: {TEXT}; }}
  .stSelectbox label {{ color: {SUBTEXT} !important; }}
</style>
""", unsafe_allow_html=True)


# ── Load & derive all data from real CSVs ─────────────────────────────────────
@st.cache_data
def load_data():
    # ── Level 3: individual sale / event rows ──────────────────────────────
    CP_FILE_ID = "1OIchAx6pC7YJtckunPgVAt5-23hx9jTp"
    cp1 = pd.read_csv(f"https://drive.google.com/uc?id={CP_FILE_ID}")

    bayc1    = pd.read_csv(r"data/Level3_bayc_new.csv")

    MAYC_FILE_ID = "1Z8keoKuj6JY0VDZCZI5LDqH0lT7zP6ud"
    mayc1 = pd.read_csv(f"https://drive.google.com/uc?id={MAYC_FILE_ID}")
    
    DOODLES_FILE_ID = "16jgaH_QZS2_AUjv-NpM2JoZ0UwS9Xodm"
    doodles1 = pd.read_csv(f"https://drive.google.com/uc?id={DOODLES_FILE_ID}")

    PP_FILE_ID = "1NWKCaKszVV4pEXVEVO1UKkHRdWEyF3Ay"
    pp1 = pd.read_csv(f"https://drive.google.com/uc?id={PP_FILE_ID}")

    cp1["collection"]      = "CryptoPunks"
    bayc1["collection"]    = "BAYC"
    mayc1["collection"]    = "MAYC"
    doodles1["collection"] = "Doodles"
    pp1["collection"]      = "Pudgy Penguins"

    sales_df = pd.concat([cp1, bayc1, mayc1, doodles1, pp1], ignore_index=True)

    # ── Level 4: per-NFT aggregated stats ──────────────────────────────────
    cp2      = pd.read_csv(r"data/Level4_cryptopunks_new.csv")
    bayc2    = pd.read_csv(r"data/Level4_bayc_new.csv")
    mayc2    = pd.read_csv(r"data/Level4_mayc_new.csv")
    doodles2 = pd.read_csv(r"data/Level4_doodles_new.csv")
    pp2      = pd.read_csv(r"data/Level4_pudgypenguins_new.csv")

    cp2["collection"]      = "CryptoPunks"
    bayc2["collection"]    = "BAYC"
    mayc2["collection"]    = "MAYC"
    doodles2["collection"] = "Doodles"
    pp2["collection"]      = "Pudgy Penguins"

    agg_df = pd.concat([cp2, bayc2, mayc2, doodles2, pp2], ignore_index=True)

    # ── Clean types ─────────────────────────────────────────────────────────
    sales_df["price_eth"] = pd.to_numeric(sales_df["price_eth"], errors="coerce")
    sales_df["timestamp"] = pd.to_datetime(sales_df["timestamp"],  errors="coerce")

    for col in ["total_volume_eth", "avg_price_eth", "max_price_eth",
                "min_price_eth", "transaction_count"]:
        if col in agg_df.columns:
            agg_df[col] = pd.to_numeric(agg_df[col], errors="coerce")

    return sales_df, agg_df


sales_df, agg_df = load_data()

# ── Derive all downstream frames from real data ───────────────────────────────

# sales-only rows
sales = sales_df[sales_df["event_type"].fillna("").str.lower() == "sale"].copy()

# ── coll_data: one row per collection summary (used by Sales/Price/Volume tabs)
coll_data = (
    agg_df.groupby("collection", as_index=False)
    .agg(
        total_volume=("total_volume_eth",   "sum"),
        avg_price   =("avg_price_eth",      "mean"),
        max_price   =("max_price_eth",      "max"),
        min_price   =("min_price_eth",      "min"),
        avg_tx      =("transaction_count",  "mean"),
    )
    .round({"avg_price": 2, "avg_tx": 1})
)

# ── trends: monthly volume / avg price / sales count
sales["month"] = sales["timestamp"].dt.to_period("M").astype(str)
monthly_grp    = sales.groupby("month")
trends = pd.DataFrame({
    "month":       monthly_grp["price_eth"].sum().index,
    "volume":      monthly_grp["price_eth"].sum().values,
    "avg_price":   monthly_grp["price_eth"].mean().values,
    "sales_count": monthly_grp["price_eth"].count().values,
}).sort_values("month").reset_index(drop=True)

# ── top_vol: top 10 NFTs by total_volume_eth (from agg_df)
_id_col = "identifier" if "identifier" in agg_df.columns else agg_df.columns[0]
top_vol = (
    agg_df[[_id_col, "collection", "total_volume_eth", "avg_price_eth"]]
    .dropna(subset=["total_volume_eth"])
    .sort_values("total_volume_eth", ascending=False)
    .head(10)
    .reset_index(drop=True)
    .rename(columns={_id_col: "id", "total_volume_eth": "volume",
                     "avg_price_eth": "avg_price"})
)

# ── top_tx_nfts: top 10 NFTs by transaction_count
top_tx_nfts = (
    agg_df[[_id_col, "collection", "transaction_count",
            "total_volume_eth", "avg_price_eth"]]
    .dropna(subset=["transaction_count"])
    .sort_values("transaction_count", ascending=False)
    .head(10)
    .reset_index(drop=True)
    .rename(columns={_id_col: "id", "transaction_count": "tx",
                     "total_volume_eth": "vol", "avg_price_eth": "avg"})
)
# keep top_tx as alias for backward compat
top_tx = top_tx_nfts.copy()

# ── top_high / top_low: top 10 NFTs by max / min price
top_high = (
    agg_df[[_id_col, "collection", "max_price_eth"]]
    .dropna(subset=["max_price_eth"])
    .sort_values("max_price_eth", ascending=False)
    .head(10)
    .reset_index(drop=True)
    .rename(columns={_id_col: "id", "max_price_eth": "value"})
)
top_low = (
    agg_df[[_id_col, "min_price_eth"]]
    .dropna(subset=["min_price_eth"])
    .query("min_price_eth > 0")
    .sort_values("min_price_eth")
    .head(10)
    .reset_index(drop=True)
    .rename(columns={_id_col: "id", "min_price_eth": "value"})
)

# ── event counts (for Event Analysis tab)
event_counts = sales_df["event_type"].fillna("unknown").str.lower().value_counts()
evt_labels   = [e.capitalize() for e in event_counts.index.tolist()]
evt_values   = event_counts.values.tolist()

# ── notable events
sale_events = sales_df[sales_df["event_type"].fillna("").str.lower() == "sale"]
transfer_ev = sales_df[sales_df["event_type"].fillna("").str.lower() == "transfer"]
mint_ev     = sales_df[sales_df["event_type"].fillna("").str.lower() == "mint"]

def _fmt_id(row):
    """Build a readable NFT label from whatever identifier columns exist."""
    for col in ["identifier", "token_id", "id", "nft_id"]:
        if col in row.index and pd.notna(row[col]):
            return f"{row.get('collection', '')} #{row[col]}"
    return str(row.get("collection", "—"))

highest_sale_row   = sale_events.loc[sale_events["price_eth"].idxmax()] if len(sale_events) else None
last_transfer_row  = transfer_ev.sort_values("timestamp").iloc[-1] if len(transfer_ev) else None
last_mint_row      = mint_ev.sort_values("timestamp").iloc[-1]     if len(mint_ev)     else None


# ── Sidebar collection filter ─────────────────────────────────────────────────
available_colls = sorted(coll_data["collection"].dropna().unique().tolist())

with st.sidebar:
    st.markdown(f"<div style='color:{SUBTEXT};font-size:12px;margin-bottom:8px;'>COLLECTION FILTER</div>",
                unsafe_allow_html=True)
    sel = st.selectbox("", ["All"] + available_colls, label_visibility="collapsed")

filt = coll_data if sel == "All" else coll_data[coll_data["collection"] == sel]

# Re-derive trends for the selected collection
filt_sales = sales.copy() if sel == "All" else sales[sales["collection"] == sel].copy()
if len(filt_sales):
    filt_sales["month"] = filt_sales["timestamp"].dt.to_period("M").astype(str)
    _mg = filt_sales.groupby("month")
    trends = pd.DataFrame({
        "month":       _mg["price_eth"].sum().index,
        "volume":      _mg["price_eth"].sum().values,
        "avg_price":   _mg["price_eth"].mean().values,
        "sales_count": _mg["price_eth"].count().values,
    }).sort_values("month").reset_index(drop=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

# ✅ NEW: HEX → RGBA converter
def hex_to_rgba(hex_color, alpha=0.1):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def dark_layout(fig, height=260):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font_color=SUBTEXT,
            font_size=11,
            orientation="h",
            y=-0.22,
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(0,0,0,0)",
        linecolor=BORDER,
        tickfont=dict(color=TICK, size=10),
        tickangle=45,
    )
    fig.update_yaxes(
        gridcolor=GRID,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(color=TICK, size=11),
    )
    return fig


def bar_fig(x, y, colors, height=240):
    fig = go.Figure(go.Bar(x=x, y=y, marker_color=colors,
                            marker_line_width=0))
    return dark_layout(fig, height)


# ✅ FIXED FUNCTION (THIS WAS CAUSING ERROR)
def line_fig(x, ys_dict, height=260):
    """ys_dict: {label: (values, colour)}"""
    fig = go.Figure()

    for label, (vals, colour) in ys_dict.items():

        # ✅ FIX: Proper color handling
        if colour.startswith("#"):
            fill_col = hex_to_rgba(colour, 0.1)
        elif colour.startswith("rgb"):
            fill_col = colour.replace("rgb", "rgba").replace(")", ",0.1)")
        else:
            fill_col = colour

        fig.add_trace(go.Scatter(
            x=x,
            y=vals,
            name=label,
            mode="lines+markers",
            line=dict(color=colour, width=2),
            marker=dict(size=3, color=colour),
            fill="tozeroy",
            fillcolor=fill_col,  # ✅ FIXED HERE
        ))

    return dark_layout(fig, height)





def metric_card(label, value, unit=""):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-unit">{unit}</div>
    </div>"""


def card(content_html):
    return f'<div class="card-wrap">{content_html}</div>'


def chart_title(t):
    return f'<div class="chart-title">{t}</div>'


def badge(collection):
    c = CMAP.get(collection, "#888")
    return f'<span class="coll-badge" style="background:{c}22;color:{c}">{collection}</span>'


# ── Dashboard header ──────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <div class="dash-logo">📊</div>
  <div>
    <div class="dash-title">NFT Market Analytics</div>
    <div class="dash-sub">5 Collections &nbsp;·&nbsp; CryptoPunks &nbsp;·&nbsp; BAYC &nbsp;·&nbsp; MAYC &nbsp;·&nbsp; Doodles &nbsp;·&nbsp; Pudgy Penguins</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Sales & Revenue",
    "📉 Market Trends",
    "🔔 Event Analysis",
    "💰 Price Analysis",
    "📦 Volume Analysis",
    "🏆 Top 10 Rankings",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Sales & Revenue
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    _filt_sales = filt_sales if len(filt_sales) else sales
    total_vol   = round(_filt_sales["price_eth"].sum(), 2)
    total_sales = len(_filt_sales)
    avg_p       = round(_filt_sales["price_eth"].mean(), 2)
    max_p       = round(_filt_sales["price_eth"].max(), 2)
    max_coll    = (_filt_sales.loc[_filt_sales["price_eth"].idxmax(), "collection"]
                   if len(_filt_sales) else "—")

    def _fmt_vol(v):
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000:     return f"{v/1_000:.1f}K"
        return str(round(v, 2))

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Total Volume",   _fmt_vol(total_vol), "ETH across all collections"), unsafe_allow_html=True)
    c2.markdown(metric_card("Total Sales",    _fmt_vol(total_sales), "transactions"),              unsafe_allow_html=True)
    c3.markdown(metric_card("Avg Sale Price", f"{avg_p}",           "ETH"),                       unsafe_allow_html=True)
    c4.markdown(metric_card("Highest Sale",   f"{max_p:,}",         f"ETH ({max_coll})"),         unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown(chart_title("Total volume by collection (ETH)"), unsafe_allow_html=True)
        colors = [CMAP[c] for c in filt["collection"]]
        fig = bar_fig(filt["collection"].tolist(), filt["total_volume"].tolist(), colors)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cb:
        st.markdown(chart_title("Average sale price by collection (ETH)"), unsafe_allow_html=True)
        fig2 = bar_fig(filt["collection"].tolist(), filt["avg_price"].tolist(), colors)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown(chart_title("Highest sale price by collection (ETH)"), unsafe_allow_html=True)
    fig3 = bar_fig(filt["collection"].tolist(), filt["max_price"].tolist(), colors, height=700)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Market Trends
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if len(trends):
        peak_month     = trends.loc[trends["volume"].idxmax(), "month"]
        peak_vol_val   = round(trends["volume"].max(), 1)
        avg_monthly    = int(trends["sales_count"].mean())
        peak_avg_month = trends.loc[trends["avg_price"].idxmax(), "month"]
        peak_avg_val   = round(trends["avg_price"].max(), 1)
    else:
        peak_month = peak_avg_month = "—"
        peak_vol_val = avg_monthly = peak_avg_val = 0

    c1, c2, c3 = st.columns(3)
    c1.markdown(metric_card("Peak Volume Month", peak_month,    f"{_fmt_vol(peak_vol_val)} ETH"), unsafe_allow_html=True)
    c2.markdown(metric_card("Avg Monthly Sales", f"{avg_monthly:,}", "transactions / month"),     unsafe_allow_html=True)
    c3.markdown(metric_card("Peak Avg Price",    f"{peak_avg_val}", f"ETH ({peak_avg_month})"),   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(chart_title("Monthly trading volume (ETH)"), unsafe_allow_html=True)
    fig = line_fig(trends["month"], {"Volume": (trends["volume"].tolist(), "#534AB7")}, height=280)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    ca, cb = st.columns(2)
    with ca:
        st.markdown(chart_title("Monthly average price (ETH)"), unsafe_allow_html=True)
        fig2 = line_fig(trends["month"], {"Avg Price": (trends["avg_price"].tolist(), "#1D9E75")})
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    with cb:
        st.markdown(chart_title("Monthly sales activity (count)"), unsafe_allow_html=True)
        fig3 = line_fig(trends["month"], {"Sales": (trends["sales_count"].tolist(), "#D85A30")})
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Event Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    total_events    = len(sales_df)
    sales_count_ev  = event_counts.get("sale",     event_counts.get("sales",    0))
    transfer_count  = event_counts.get("transfer", event_counts.get("transfers",0))
    mint_count      = event_counts.get("mint",     event_counts.get("mints",    0))

    def _pct(n, total): return f"{round(n/total*100)}% of total" if total else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Total Events",    _fmt_vol(total_events),   "all types"),                      unsafe_allow_html=True)
    c2.markdown(metric_card("Sales Events",    _fmt_vol(sales_count_ev), _pct(sales_count_ev, total_events)), unsafe_allow_html=True)
    c3.markdown(metric_card("Transfer Events", _fmt_vol(transfer_count), _pct(transfer_count, total_events)), unsafe_allow_html=True)
    c4.markdown(metric_card("Mint Events",     _fmt_vol(mint_count),     _pct(mint_count, total_events)),     unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)

    with ca:
        st.markdown(chart_title("Event type distribution"), unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=evt_labels,
            values=evt_values,
            marker=dict(colors=["#1D9E75", "#534AB7", "#BA7517", "#D85A30", "#D4537E"],
                        line=dict(color=CARD_BG, width=2)),
            hole=0.55,
            textfont=dict(color=TEXT),
        ))
        dark_layout(fig, 280)
        fig.update_layout(legend=dict(orientation="h", y=-0.15, font_color=SUBTEXT, font_size=12))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cb:
        st.markdown(chart_title("Highest sale per collection (ETH)"), unsafe_allow_html=True)
        colors = [CMAP.get(c, "#888") for c in filt["collection"]]
        fig2 = bar_fig(filt["collection"].tolist(), filt["max_price"].tolist(), colors, 280)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Notable events — fully from real data
    hs_label  = _fmt_id(highest_sale_row)  if highest_sale_row  is not None else "—"
    hs_val    = f"{round(highest_sale_row['price_eth'], 2)} ETH" if highest_sale_row is not None else "—"
    lt_label  = _fmt_id(last_transfer_row) if last_transfer_row is not None else "—"
    lt_date   = str(last_transfer_row["timestamp"])[:10] if last_transfer_row is not None else "—"
    lm_label  = _fmt_id(last_mint_row)     if last_mint_row     is not None else "—"
    lm_date   = str(last_mint_row["timestamp"])[:10]    if last_mint_row     is not None else "—"

    notable = [
        ("Highest Sale",         hs_label, hs_val),
        ("Most Recent Transfer", lt_label, lt_date),
        ("Most Recent Mint",     lm_label, lm_date),
        ("Collections Tracked",  ", ".join(available_colls), str(len(available_colls))),
    ]
    rows = "".join(
        f"<tr><td>{r[0]}</td><td style='color:#aaa'>{r[1]}</td>"
        f"<td style='text-align:right;color:#ccc'>{r[2]}</td></tr>"
        for r in notable
    )
    st.markdown(f"""
    <div class="card-wrap" style="padding:1rem 1.25rem">
      <table class="styled-table">{rows}</table>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Price Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    global_avg = round(filt["avg_price"].mean(), 2)
    global_max = round(filt["max_price"].max(), 2)
    global_min = round(filt["min_price"].min(), 4)
    total_vol4 = _fmt_vol(filt["total_volume"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Global Avg Price", f"{global_avg}", "ETH"), unsafe_allow_html=True)
    c2.markdown(metric_card("Global Max Price", f"{global_max:,}", "ETH"), unsafe_allow_html=True)
    c3.markdown(metric_card("Global Min Price", f"{global_min}", "ETH"),  unsafe_allow_html=True)
    c4.markdown(metric_card("Total Volume",     total_vol4,      "ETH"),  unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)

    with ca:
        st.markdown(chart_title("Top 10 highest value NFTs (max price ETH)"), unsafe_allow_html=True)
        colors_high = [CMAP.get(c, "#534AB7") for c in top_high["collection"]]
        fig = bar_fig(top_high["id"].tolist(), top_high["value"].tolist(), colors_high)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cb:
        st.markdown(chart_title("Top 10 lowest value NFTs (min price ETH)"), unsafe_allow_html=True)
        fig2 = bar_fig(top_low["id"].tolist(), top_low["value"].tolist(), "#888780")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown(chart_title("Price comparison by collection (avg / max÷10 / min)"), unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Avg Price", x=filt["collection"], y=filt["avg_price"],
                           marker_color="#534AB7"))
    fig3.add_trace(go.Bar(name="Max Price (÷10)", x=filt["collection"],
                           y=(filt["max_price"] / 10).round(2), marker_color="#1D9E75"))
    fig3.add_trace(go.Bar(name="Min Price", x=filt["collection"], y=filt["min_price"],
                           marker_color="#D85A30"))
    fig3.update_layout(barmode="group")
    dark_layout(fig3, 240)
    fig3.update_layout(legend=dict(orientation="h", y=-0.22, font_color=SUBTEXT, font_size=11))
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Volume Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    top_vol_nft    = top_vol.iloc[0]["id"]       if len(top_vol)     else "—"
    top_vol_eth    = _fmt_vol(top_vol.iloc[0]["volume"]) if len(top_vol) else "—"
    most_traded    = top_tx_nfts.iloc[0]["id"]   if len(top_tx_nfts) else "—"
    most_traded_tx = top_tx_nfts.iloc[0]["tx"]   if len(top_tx_nfts) else 0
    avg_tx_all     = round(filt["avg_tx"].mean(), 1)

    c1, c2, c3 = st.columns(3)
    c1.markdown(metric_card("Top Volume NFT",  top_vol_nft,         f"~{top_vol_eth} ETH total"),      unsafe_allow_html=True)
    c2.markdown(metric_card("Most Traded NFT", most_traded,         f"{most_traded_tx} transactions"), unsafe_allow_html=True)
    c3.markdown(metric_card("Avg Txn/NFT",     f"{avg_tx_all}",     "transactions"),                   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)

    with ca:
        st.markdown(chart_title("Top 10 most transacted NFTs"), unsafe_allow_html=True)
        colors_tx = [CMAP[c] for c in top_tx_nfts["collection"]]
        fig = bar_fig(top_tx_nfts["id"].tolist(), top_tx_nfts["tx"].tolist(), colors_tx)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cb:
        st.markdown(chart_title("Top 10 highest volume NFTs (ETH)"), unsafe_allow_html=True)
        colors_vol = [CMAP[c] for c in top_vol["collection"]]
        fig2 = bar_fig(top_vol["id"].tolist(), top_vol["volume"].tolist(), colors_vol)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    ca2, cb2 = st.columns(2)
    with ca2:
        st.markdown(chart_title("Total volume by collection (ETH)"), unsafe_allow_html=True)
        colors = [CMAP[c] for c in filt["collection"]]
        fig3 = bar_fig(filt["collection"].tolist(), filt["total_volume"].tolist(), colors, 200)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with cb2:
        st.markdown(chart_title("Avg transactions per NFT by collection"), unsafe_allow_html=True)
        fig4 = bar_fig(filt["collection"].tolist(), filt["avg_tx"].tolist(), colors, 200)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Top 10 Rankings
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    ca, cb = st.columns(2)

    # -- Top 10 by Volume table
    with ca:
        rows_vol = ""
        for i, row in top_vol.reset_index(drop=True).iterrows():
            rows_vol += (f"<tr><td class='rank'>{i+1}</td><td>{row['id']}</td>"
                         f"<td>{badge(row['collection'])}</td>"
                         f"<td class='num-right'>{round(row['volume'],2):,}</td></tr>")
        st.markdown(f"""
        <div class="card-wrap" style="padding:1rem 1.25rem">
          <div style="font-size:13px;font-weight:500;color:#ccc;margin-bottom:8px">Top 10 by volume (ETH)</div>
          <table class="styled-table">
            <thead><tr><th>#</th><th>NFT ID</th><th>Collection</th><th style="text-align:right">Volume (ETH)</th></tr></thead>
            <tbody>{rows_vol}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)

    # -- Top 10 by Avg Price table (derived from agg_df)
    with cb:
        top_avg = (
            agg_df[[_id_col, "collection", "avg_price_eth"]]
            .dropna(subset=["avg_price_eth"])
            .sort_values("avg_price_eth", ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        rows_avg = ""
        for i, row in top_avg.iterrows():
            rows_avg += (f"<tr><td class='rank'>{i+1}</td><td>{row[_id_col]}</td>"
                         f"<td>{badge(row['collection'])}</td>"
                         f"<td class='num-right'>{round(row['avg_price_eth'],2)}</td></tr>")
        st.markdown(f"""
        <div class="card-wrap" style="padding:1rem 1.25rem">
          <div style="font-size:13px;font-weight:500;color:#ccc;margin-bottom:8px">Top 10 by avg price (ETH)</div>
          <table class="styled-table">
            <thead><tr><th>#</th><th>NFT ID</th><th>Collection</th><th style="text-align:right">Avg Price</th></tr></thead>
            <tbody>{rows_avg}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)

    # -- Top 10 by Transaction Count table
    rows_tx = ""
    for i, row in top_tx_nfts.reset_index(drop=True).iterrows():
        rows_tx += (f"<tr><td class='rank'>{i+1}</td><td>{row['id']}</td>"
                    f"<td>{badge(row['collection'])}</td>"
                    f"<td class='num-right-dim'>{int(row['tx'])}</td>"
                    f"<td class='num-right-dim'>{round(row['vol'],2):,}</td>"
                    f"<td class='num-right-dim'>{round(row['avg'],2)}</td></tr>")
    st.markdown(f"""
    <div class="card-wrap" style="padding:1rem 1.25rem">
      <div style="font-size:13px;font-weight:500;color:#ccc;margin-bottom:8px">Top 10 by transaction count</div>
      <table class="styled-table">
        <thead><tr><th>#</th><th>NFT ID</th><th>Collection</th>
          <th style="text-align:right">Txns</th>
          <th style="text-align:right">Volume (ETH)</th>
          <th style="text-align:right">Avg Price</th></tr></thead>
        <tbody>{rows_tx}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)

    # -- Combined chart — normalise so all three series are on a comparable scale
    if len(top_tx_nfts):
        _ids   = top_tx_nfts["id"].tolist()
        _tx10  = [round(v / 10, 1) for v in top_tx_nfts["tx"].tolist()]
        _vol100= [round(v / 100, 1) for v in top_tx_nfts["vol"].tolist()]
        _avg   = top_tx_nfts["avg"].round(1).tolist()

        st.markdown(chart_title("Top 10 combined rank — volume÷100, avg price & tx÷10"), unsafe_allow_html=True)
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(name="Vol / 100 ETH",  x=_ids, y=_vol100, marker_color="#534AB7"))
        fig_c.add_trace(go.Bar(name="Avg Price ETH",  x=_ids, y=_avg,    marker_color="#1D9E75"))
        fig_c.add_trace(go.Bar(name="Tx Count / 10",  x=_ids, y=_tx10,   marker_color="#D85A30"))
        fig_c.update_layout(barmode="group")
        dark_layout(fig_c, 280)
        fig_c.update_layout(legend=dict(orientation="h", y=-0.22, font_color=SUBTEXT, font_size=11))
        st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})
