import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy · Shipping Route Efficiency",
    page_icon="NC",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# US STATE NAME → CODE MAPPING
# ──────────────────────────────────────────────
STATE_CODE_MAP = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1321 0%, #131b2e 100%);
    border-right: 1px solid rgba(0, 212, 170, 0.12);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00D4AA;
}

/* ── KPI Metric Cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(26, 31, 46, 0.95) 0%, rgba(20, 27, 45, 0.85) 100%);
    border: 1px solid rgba(0, 212, 170, 0.18);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: transform 0.3s cubic-bezier(.4,0,.2,1), box-shadow 0.3s cubic-bezier(.4,0,.2,1);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0, 212, 170, 0.15), inset 0 1px 0 rgba(255,255,255,0.08);
    border-color: rgba(0, 212, 170, 0.35);
}
div[data-testid="stMetric"] label {
    color: #8892a4 !important;
    font-weight: 500;
    font-size: 0.82rem;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
    font-size: 1.75rem;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-weight: 600;
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.3px;
    color: #8892a4;
    border-radius: 10px 10px 0 0;
    padding: 12px 28px;
    transition: all 0.3s ease;
}
button[data-baseweb="tab"]:hover {
    color: #00D4AA;
    background: rgba(0, 212, 170, 0.06);
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00D4AA !important;
    border-bottom: 3px solid #00D4AA;
    background: rgba(0, 212, 170, 0.08);
}

/* ── Dataframes ── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(0, 212, 170, 0.12);
}

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0 4px 0;
    margin-bottom: 8px;
    border-bottom: 2px solid rgba(0, 212, 170, 0.15);
}
.section-header h3 {
    margin: 0;
    color: #e0e0e0;
    font-weight: 700;
    font-size: 1.15rem;
}

/* ── Plotly chart containers ── */
.stPlotlyChart {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(0, 212, 170, 0.08);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    transition: box-shadow 0.3s ease;
}
.stPlotlyChart:hover {
    box-shadow: 0 8px 32px rgba(0, 212, 170, 0.1);
}

/* ── Title area ── */
.dashboard-title {
    text-align: center;
    padding: 8px 0 0 0;
}
.dashboard-title h1 {
    background: linear-gradient(135deg, #00D4AA 0%, #00b4d8 50%, #7B61FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.1rem;
    margin-bottom: 2px;
}
.dashboard-title p {
    color: #6b7280;
    font-size: 0.95rem;
    font-weight: 400;
}

/* ── Dividers ── */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,170,0.25), transparent);
    margin: 24px 0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PLOTLY THEME HELPERS
# ──────────────────────────────────────────────
TEAL = "#00D4AA"
AMBER = "#FFB347"
CORAL = "#FF6B6B"
PURPLE = "#7B61FF"
CYAN = "#00b4d8"
PALETTE = [TEAL, AMBER, PURPLE, CORAL, CYAN, "#36CFC9", "#FFC069", "#B37FEB", "#FF85C0", "#69C0FF"]

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#c9d1d9"),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#1A1F2E",
        bordercolor=TEAL,
        font=dict(family="Inter", size=13, color="#e0e0e0"),
    ),
)


def apply_layout(fig, **kwargs):
    """Apply consistent dark theme to any plotly figure."""
    layout = {**PLOTLY_LAYOUT, **kwargs}
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)
    return fig


# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "Nassau_Candy_Preprocessed.csv")
    df = pd.read_csv(data_path)
    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", dayfirst=False)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed", dayfirst=False)
    # State code for choropleth
    df["State_Code"] = df["State/Province"].map(STATE_CODE_MAP)
    return df


df_raw = load_data()

# ──────────────────────────────────────────────
# SIDEBAR FILTERS
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    # ── Date Range ──
    st.markdown("#### Date Range")
    min_date = df_raw["Order Date"].min().date()
    max_date = df_raw["Order Date"].max().date()
    date_range = st.date_input(
        "Order date window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range",
    )

    st.markdown("---")

    # ── Region / State ──
    st.markdown("#### Region & State")
    all_regions = sorted(df_raw["Region"].unique())
    selected_regions = st.multiselect("Region", all_regions, default=all_regions, key="regions")

    states_in_regions = sorted(
        df_raw[df_raw["Region"].isin(selected_regions)]["State/Province"].unique()
    )
    selected_states = st.multiselect("State / Province", states_in_regions, default=states_in_regions, key="states")

    st.markdown("---")

    # ── Ship Mode ──
    st.markdown("#### Ship Mode")
    all_modes = sorted(df_raw["Ship Mode"].unique())
    selected_modes = st.multiselect("Ship Mode", all_modes, default=all_modes, key="ship_modes")

    st.markdown("---")

    # ── Division ──
    st.markdown("#### Division")
    all_divisions = sorted(df_raw["Division"].unique())
    selected_divisions = st.multiselect("Division", all_divisions, default=all_divisions, key="divisions")

    st.markdown("---")

    # ── Lead-time Threshold ──
    st.markdown("#### Lead-Time Threshold")
    min_days = int(df_raw["Shipping Days"].min())
    max_days = int(df_raw["Shipping Days"].max())
    lead_time_range = st.slider(
        "Shipping Days range",
        min_value=min_days,
        max_value=max_days,
        value=(min_days, max_days),
        key="lead_time",
    )

    st.markdown("---")

    # ── Executive Summary Download ──
    st.markdown("#### 📄 Reports")
    exec_summary_path = os.path.join(os.path.dirname(__file__), "executive_summary.html")
    if os.path.exists(exec_summary_path):
        with open(exec_summary_path, "r", encoding="utf-8") as f:
            exec_html = f.read()
        st.download_button(
            label="⬇ Download Executive Summary",
            data=exec_html,
            file_name="Nassau_Candy_Executive_Summary.html",
            mime="text/html",
            key="dl_exec_summary",
        )

# ── Apply Filters ──
mask = (
    (df_raw["Region"].isin(selected_regions))
    & (df_raw["State/Province"].isin(selected_states))
    & (df_raw["Ship Mode"].isin(selected_modes))
    & (df_raw["Division"].isin(selected_divisions))
    & (df_raw["Shipping Days"] >= lead_time_range[0])
    & (df_raw["Shipping Days"] <= lead_time_range[1])
)

if len(date_range) == 2:
    mask = mask & (
        (df_raw["Order Date"].dt.date >= date_range[0])
        & (df_raw["Order Date"].dt.date <= date_range[1])
    )

df = df_raw[mask].copy()

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown(
    """
    <div class="dashboard-title">
        <h1>Nassau Candy &middot; Shipping Route Efficiency</h1>
        <p>Factory-to-Customer Shipping Route Performance Analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Quick stats bar ──
if df.empty:
    st.warning("No data matches your current filters. Please adjust the sidebar filters.")
    st.stop()

total_orders = len(df)
avg_ship_days = df["Shipping Days"].mean()
avg_efficiency = df["Route Efficiency Score"].mean()
on_time_rate = (df["Delay Status"] == "On-Time").mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Avg Shipping Days", f"{avg_ship_days:,.0f}")
col3.metric("Avg Efficiency Score", f"{avg_efficiency:.2f}")
col4.metric("On-Time Rate", f"{on_time_rate:.1f}%")

st.markdown("---")

# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Route Efficiency Overview",
    "Geographic Shipping Map",
    "Ship Mode Comparison",
    "Route Drill-Down",
    "Trend & Seasonality",
    "Profitability & Cost",
])

# ══════════════════════════════════════════════
# TAB 1 — ROUTE EFFICIENCY OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header"><h3>Average Lead Time by Route</h3></div>', unsafe_allow_html=True)

    route_stats = (
        df.groupby("Route_Region_State")
        .agg(
            Avg_Shipping_Days=("Shipping Days", "mean"),
            Avg_Efficiency=("Route Efficiency Score", "mean"),
            Orders=("Row ID", "count"),
            On_Time_Pct=("Delay Flag", lambda x: (1 - x.mean()) * 100),
        )
        .reset_index()
        .sort_values("Avg_Shipping_Days", ascending=False)
    )

    top_routes = route_stats.head(20)

    fig_lead = px.bar(
        top_routes,
        x="Avg_Shipping_Days",
        y="Route_Region_State",
        orientation="h",
        color="Avg_Shipping_Days",
        color_continuous_scale=[[0, TEAL], [0.5, AMBER], [1, CORAL]],
        custom_data=["Orders", "Avg_Efficiency", "On_Time_Pct"],
    )
    fig_lead.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg Shipping Days: <b>%{x:.0f}</b><br>"
            "Orders: <b>%{customdata[0]:,}</b><br>"
            "Efficiency Score: <b>%{customdata[1]:.2f}</b><br>"
            "On-Time: <b>%{customdata[2]:.1f}%</b>"
            "<extra></extra>"
        )
    )
    apply_layout(fig_lead, title="Top 20 Routes by Average Lead Time", height=580,
                 coloraxis_colorbar=dict(title="Days", thickness=12))
    fig_lead.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_lead, use_container_width=True)

    # ── Leaderboard ──
    st.markdown('<div class="section-header"><h3>Route Performance Leaderboard</h3></div>', unsafe_allow_html=True)

    leaderboard = route_stats.sort_values("Avg_Efficiency", ascending=False).reset_index(drop=True)
    leaderboard.index += 1
    leaderboard.columns = ["Route", "Avg Shipping Days", "Avg Efficiency Score", "Orders", "On-Time %"]
    leaderboard["Avg Shipping Days"] = leaderboard["Avg Shipping Days"].round(0).astype(int)
    leaderboard["Avg Efficiency Score"] = leaderboard["Avg Efficiency Score"].round(2)
    leaderboard["On-Time %"] = leaderboard["On-Time %"].round(1)

    def color_efficiency(val):
        if val >= 22:
            return "background: linear-gradient(90deg, rgba(0,212,170,0.25), transparent); color: #00D4AA;"
        elif val >= 19:
            return "background: linear-gradient(90deg, rgba(255,179,71,0.2), transparent); color: #FFB347;"
        else:
            return "background: linear-gradient(90deg, rgba(255,107,107,0.2), transparent); color: #FF6B6B;"

    styled_lb = leaderboard.style.applymap(color_efficiency, subset=["Avg Efficiency Score"])
    st.dataframe(styled_lb, use_container_width=True, height=420)

# ══════════════════════════════════════════════
# TAB 2 — GEOGRAPHIC SHIPPING MAP
# ══════════════════════════════════════════════
with tab2:
    us_df = df.dropna(subset=["State_Code"])

    state_geo = (
        us_df.groupby(["State/Province", "State_Code"])
        .agg(
            Avg_Shipping_Days=("Shipping Days", "mean"),
            Avg_Efficiency=("Route Efficiency Score", "mean"),
            Orders=("Row ID", "count"),
            On_Time_Pct=("Delay Flag", lambda x: (1 - x.mean()) * 100),
        )
        .reset_index()
    )

    st.markdown('<div class="section-header"><h3>Shipping Lead-Time by State</h3></div>', unsafe_allow_html=True)

    map_col1, map_col2 = st.columns(2)

    with map_col1:
        fig_map1 = go.Figure(
            go.Choropleth(
                locations=state_geo["State_Code"],
                z=state_geo["Avg_Shipping_Days"],
                locationmode="USA-states",
                colorscale=[[0, "#0d9488"], [0.35, "#fbbf24"], [0.65, "#f97316"], [1, "#ef4444"]],
                colorbar=dict(title="Avg Days", thickness=12, len=0.6),
                text=state_geo["State/Province"],
                customdata=state_geo[["Orders", "Avg_Efficiency", "On_Time_Pct"]].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Avg Shipping Days: <b>%{z:.0f}</b><br>"
                    "Orders: <b>%{customdata[0]:,}</b><br>"
                    "Efficiency: <b>%{customdata[1]:.2f}</b><br>"
                    "On-Time: <b>%{customdata[2]:.1f}%</b>"
                    "<extra></extra>"
                ),
            )
        )
        fig_map1.update_layout(
            title_text="Average Shipping Days",
            geo=dict(
                scope="usa",
                bgcolor="rgba(0,0,0,0)",
                lakecolor="rgba(0,0,0,0)",
                landcolor="#1A1F2E",
                showlakes=True,
            ),
            **PLOTLY_LAYOUT,
            height=460,
        )
        st.plotly_chart(fig_map1, use_container_width=True)

    with map_col2:
        fig_map2 = go.Figure(
            go.Choropleth(
                locations=state_geo["State_Code"],
                z=state_geo["Avg_Efficiency"],
                locationmode="USA-states",
                colorscale=[[0, "#ef4444"], [0.35, "#f97316"], [0.65, "#fbbf24"], [1, "#0d9488"]],
                colorbar=dict(title="Score", thickness=12, len=0.6),
                text=state_geo["State/Province"],
                customdata=state_geo[["Orders", "Avg_Shipping_Days", "On_Time_Pct"]].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Efficiency Score: <b>%{z:.2f}</b><br>"
                    "Orders: <b>%{customdata[0]:,}</b><br>"
                    "Avg Days: <b>%{customdata[1]:.0f}</b><br>"
                    "On-Time: <b>%{customdata[2]:.1f}%</b>"
                    "<extra></extra>"
                ),
            )
        )
        fig_map2.update_layout(
            title_text="Route Efficiency Score",
            geo=dict(
                scope="usa",
                bgcolor="rgba(0,0,0,0)",
                lakecolor="rgba(0,0,0,0)",
                landcolor="#1A1F2E",
                showlakes=True,
            ),
            **PLOTLY_LAYOUT,
            height=460,
        )
        st.plotly_chart(fig_map2, use_container_width=True)

    # ── Regional Bottleneck ──
    st.markdown('<div class="section-header"><h3>Regional Bottleneck Analysis</h3></div>', unsafe_allow_html=True)

    region_stats = (
        df.groupby("Region")
        .agg(
            Avg_Shipping_Days=("Shipping Days", "mean"),
            Avg_Efficiency=("Route Efficiency Score", "mean"),
            Orders=("Row ID", "count"),
            Delayed=("Delay Flag", "sum"),
        )
        .reset_index()
        .sort_values("Avg_Shipping_Days", ascending=False)
    )
    region_stats["Delay_Rate"] = (region_stats["Delayed"] / region_stats["Orders"] * 100).round(1)

    bn_col1, bn_col2 = st.columns(2)

    with bn_col1:
        fig_bn = px.bar(
            region_stats,
            x="Region",
            y="Avg_Shipping_Days",
            color="Avg_Shipping_Days",
            color_continuous_scale=[[0, TEAL], [0.5, AMBER], [1, CORAL]],
            text="Avg_Shipping_Days",
            custom_data=["Orders", "Delay_Rate"],
        )
        fig_bn.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Avg Days: <b>%{y:.0f}</b><br>"
                "Orders: <b>%{customdata[0]:,}</b><br>"
                "Delay Rate: <b>%{customdata[1]:.1f}%</b>"
                "<extra></extra>"
            ),
        )
        apply_layout(fig_bn, title="Avg Shipping Days by Region", height=400,
                     showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_bn, use_container_width=True)

    with bn_col2:
        fig_dr = px.bar(
            region_stats,
            x="Region",
            y="Delay_Rate",
            color="Delay_Rate",
            color_continuous_scale=[[0, TEAL], [0.5, AMBER], [1, CORAL]],
            text="Delay_Rate",
            custom_data=["Orders", "Avg_Shipping_Days"],
        )
        fig_dr.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Delay Rate: <b>%{y:.1f}%</b><br>"
                "Orders: <b>%{customdata[0]:,}</b><br>"
                "Avg Days: <b>%{customdata[1]:.0f}</b>"
                "<extra></extra>"
            ),
        )
        apply_layout(fig_dr, title="Delay Rate (%) by Region", height=400,
                     showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_dr, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 — SHIP MODE COMPARISON
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header"><h3>Lead Time Comparison by Ship Mode</h3></div>', unsafe_allow_html=True)

    mode_stats = (
        df.groupby("Ship Mode")
        .agg(
            Avg_Days=("Shipping Days", "mean"),
            Median_Days=("Shipping Days", "median"),
            Avg_Efficiency=("Route Efficiency Score", "mean"),
            Orders=("Row ID", "count"),
            Delayed=("Delay Flag", "sum"),
        )
        .reset_index()
    )
    mode_stats["On_Time_Pct"] = ((1 - mode_stats["Delayed"] / mode_stats["Orders"]) * 100).round(1)

    # ── KPI row per mode ──
    mode_order = ["Same Day", "First Class", "Second Class", "Standard Class"]
    mode_colors = {"Same Day": PURPLE, "First Class": TEAL, "Second Class": AMBER, "Standard Class": CORAL}

    mode_cols = st.columns(len(mode_stats))
    for i, mode in enumerate(mode_order):
        row = mode_stats[mode_stats["Ship Mode"] == mode]
        if row.empty:
            continue
        row = row.iloc[0]
        with mode_cols[i]:
            st.metric(mode, f"{row['Avg_Days']:.0f} days",
                      delta=f"{row['On_Time_Pct']:.0f}% on-time")

    sm_col1, sm_col2 = st.columns(2)

    with sm_col1:
        # ── Grouped bar ──
        fig_mode_bar = px.bar(
            mode_stats.sort_values("Avg_Days"),
            x="Ship Mode",
            y="Avg_Days",
            color="Ship Mode",
            color_discrete_sequence=[TEAL, CYAN, AMBER, CORAL],
            text="Avg_Days",
            custom_data=["Orders", "On_Time_Pct"],
        )
        fig_mode_bar.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Avg Days: <b>%{y:.0f}</b><br>"
                "Orders: <b>%{customdata[0]:,}</b><br>"
                "On-Time: <b>%{customdata[1]:.1f}%</b>"
                "<extra></extra>"
            ),
        )
        apply_layout(fig_mode_bar, title="Average Shipping Days by Mode", height=440, showlegend=False)
        st.plotly_chart(fig_mode_bar, use_container_width=True)

    with sm_col2:
        # ── Box plot ──
        fig_box = px.box(
            df,
            x="Ship Mode",
            y="Shipping Days",
            color="Ship Mode",
            color_discrete_sequence=[TEAL, CYAN, AMBER, CORAL],
            category_orders={"Ship Mode": mode_order},
        )
        fig_box.update_traces(
            hovertemplate="<b>%{x}</b><br>Shipping Days: %{y}<extra></extra>"
        )
        apply_layout(fig_box, title="Shipping Days Distribution by Mode", height=440, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Donut: delay rate per ship mode ──
    st.markdown('<div class="section-header"><h3>Delay Breakdown by Ship Mode</h3></div>', unsafe_allow_html=True)

    donut_col1, donut_col2 = st.columns([1, 1])

    with donut_col1:
        delay_by_mode = df.groupby(["Ship Mode", "Delay Status"]).size().reset_index(name="Count")
        fig_donut = px.sunburst(
            delay_by_mode,
            path=["Ship Mode", "Delay Status"],
            values="Count",
            color="Delay Status",
            color_discrete_map={"On-Time": TEAL, "Delayed": CORAL},
        )
        apply_layout(fig_donut, title="Order Distribution: Ship Mode to Delay Status", height=440)
        st.plotly_chart(fig_donut, use_container_width=True)

    with donut_col2:
        # ── Summary table ──
        summary_tbl = mode_stats[["Ship Mode", "Orders", "Avg_Days", "Median_Days", "Avg_Efficiency", "On_Time_Pct"]].copy()
        summary_tbl.columns = ["Ship Mode", "Orders", "Avg Days", "Median Days", "Avg Efficiency", "On-Time %"]
        summary_tbl["Avg Days"] = summary_tbl["Avg Days"].round(0).astype(int)
        summary_tbl["Median Days"] = summary_tbl["Median Days"].round(0).astype(int)
        summary_tbl["Avg Efficiency"] = summary_tbl["Avg Efficiency"].round(2)
        summary_tbl = summary_tbl.set_index("Ship Mode")
        st.markdown("#### Ship Mode Summary")
        st.dataframe(summary_tbl, use_container_width=True, height=360)


# ══════════════════════════════════════════════
# TAB 4 — ROUTE DRILL-DOWN
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header"><h3>State-Level Performance Insights</h3></div>', unsafe_allow_html=True)

    available_states = sorted(df["State/Province"].unique())
    selected_state = st.selectbox("Select a State / Province", available_states, key="drill_state")

    state_df = df[df["State/Province"] == selected_state].copy()

    if state_df.empty:
        st.info("No data available for the selected state with current filters.")
        st.stop()

    # ── State KPIs ──
    s_orders = len(state_df)
    s_avg_days = state_df["Shipping Days"].mean()
    s_avg_eff = state_df["Route Efficiency Score"].mean()
    s_ontime = (state_df["Delay Status"] == "On-Time").mean() * 100
    s_avg_profit = state_df["Profit Margin (%)"].mean()
    s_cities = state_df["City"].nunique()

    sk1, sk2, sk3, sk4, sk5, sk6 = st.columns(6)
    sk1.metric("Orders", f"{s_orders:,}")
    sk2.metric("Avg Ship Days", f"{s_avg_days:.0f}")
    sk3.metric("Efficiency Score", f"{s_avg_eff:.2f}")
    sk4.metric("On-Time Rate", f"{s_ontime:.1f}%")
    sk5.metric("Avg Profit Margin", f"{s_avg_profit:.1f}%")
    sk6.metric("Cities Served", f"{s_cities}")

    drill_col1, drill_col2 = st.columns(2)

    with drill_col1:
        # ── Top cities ──
        city_stats = (
            state_df.groupby("City")
            .agg(
                Orders=("Row ID", "count"),
                Avg_Days=("Shipping Days", "mean"),
                Avg_Efficiency=("Route Efficiency Score", "mean"),
            )
            .reset_index()
            .sort_values("Orders", ascending=False)
            .head(15)
        )

        fig_city = px.bar(
            city_stats,
            x="City",
            y="Orders",
            color="Avg_Days",
            color_continuous_scale=[[0, TEAL], [0.5, AMBER], [1, CORAL]],
            custom_data=["Avg_Days", "Avg_Efficiency"],
        )
        fig_city.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Orders: <b>%{y}</b><br>"
                "Avg Days: <b>%{customdata[0]:.0f}</b><br>"
                "Efficiency: <b>%{customdata[1]:.2f}</b>"
                "<extra></extra>"
            )
        )
        apply_layout(fig_city, title=f"Top Cities in {selected_state}", height=420,
                     coloraxis_colorbar=dict(title="Avg Days", thickness=10))
        fig_city.update_xaxes(tickangle=45)
        st.plotly_chart(fig_city, use_container_width=True)

    with drill_col2:
        # ── Timeline scatter ──
        fig_timeline = px.scatter(
            state_df,
            x="Order Date",
            y="Shipping Days",
            color="Delay Status",
            color_discrete_map={"On-Time": TEAL, "Delayed": CORAL},
            opacity=0.7,
            custom_data=["Order ID", "City", "Ship Mode", "Route Efficiency Score"],
        )
        fig_timeline.update_traces(
            marker=dict(size=7, line=dict(width=0.5, color="#1A1F2E")),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "City: %{customdata[1]}<br>"
                "Mode: %{customdata[2]}<br>"
                "Date: %{x|%b %d, %Y}<br>"
                "Days: <b>%{y}</b><br>"
                "Efficiency: %{customdata[3]:.2f}"
                "<extra></extra>"
            ),
        )
        apply_layout(fig_timeline, title=f"Shipment Timeline \u2014 {selected_state}", height=420)
        st.plotly_chart(fig_timeline, use_container_width=True)

    # ── Detailed data table ──
    st.markdown('<div class="section-header"><h3>Order-Level Shipment Details</h3></div>', unsafe_allow_html=True)

    display_cols = [
        "Order ID", "Order Date", "Ship Date", "Ship Mode", "City",
        "Division", "Product Name", "Shipping Days", "Route Efficiency Score",
        "Delay Status", "Profit Margin (%)", "Sales", "Units",
    ]
    detail_df = state_df[display_cols].sort_values("Order Date", ascending=False).reset_index(drop=True)
    detail_df["Order Date"] = detail_df["Order Date"].dt.strftime("%b %d, %Y")
    detail_df["Ship Date"] = detail_df["Ship Date"].dt.strftime("%b %d, %Y")

    st.dataframe(
        detail_df,
        use_container_width=True,
        height=450,
        column_config={
            "Sales": st.column_config.NumberColumn("Sales ($)", format="$%.2f"),
            "Profit Margin (%)": st.column_config.NumberColumn("Margin %", format="%.1f%%"),
            "Route Efficiency Score": st.column_config.ProgressColumn(
                "Efficiency",
                min_value=0,
                max_value=float(df_raw["Route Efficiency Score"].max()),
                format="%.2f",
            ),
        },
    )

# ══════════════════════════════════════════════
# TAB 5 — TREND & SEASONALITY ANALYSIS
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header"><h3>Monthly Shipping Volume Trend</h3></div>', unsafe_allow_html=True)

    # ── Monthly volume line chart ──
    monthly_vol = (
        df.groupby([df["Order Date"].dt.to_period("M")])
        .agg(Orders=("Row ID", "count"), Avg_Days=("Shipping Days", "mean"))
        .reset_index()
    )
    monthly_vol["Order Date"] = monthly_vol["Order Date"].astype(str)

    fig_vol = make_subplots(specs=[[{"secondary_y": True}]])
    fig_vol.add_trace(
        go.Bar(
            x=monthly_vol["Order Date"],
            y=monthly_vol["Orders"],
            name="Orders",
            marker_color=TEAL,
            opacity=0.7,
            hovertemplate="<b>%{x}</b><br>Orders: <b>%{y:,}</b><extra></extra>",
        ),
        secondary_y=False,
    )
    fig_vol.add_trace(
        go.Scatter(
            x=monthly_vol["Order Date"],
            y=monthly_vol["Avg_Days"],
            name="Avg Shipping Days",
            mode="lines+markers",
            line=dict(color=CORAL, width=2.5),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>Avg Days: <b>%{y:.0f}</b><extra></extra>",
        ),
        secondary_y=True,
    )
    apply_layout(fig_vol, title="Monthly Order Volume & Average Lead Time", height=440)
    fig_vol.update_yaxes(title_text="Orders", secondary_y=False)
    fig_vol.update_yaxes(title_text="Avg Shipping Days", secondary_y=True)
    st.plotly_chart(fig_vol, use_container_width=True)

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        # ── Seasonal delay heatmap ──
        st.markdown('<div class="section-header"><h3>Seasonal Delay Heatmap</h3></div>', unsafe_allow_html=True)

        heat_data = df.copy()
        heat_data["Month"] = heat_data["Order Date"].dt.month_name().str[:3]
        heat_data["Month_Num"] = heat_data["Order Date"].dt.month
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        heatmap_df = (
            heat_data.groupby(["Ship Mode", "Month", "Month_Num"])
            .agg(Delay_Rate=("Delay Flag", "mean"))
            .reset_index()
            .sort_values("Month_Num")
        )
        heatmap_df["Delay_Rate"] = (heatmap_df["Delay_Rate"] * 100).round(1)

        heatmap_pivot = heatmap_df.pivot(index="Ship Mode", columns="Month", values="Delay_Rate")
        heatmap_pivot = heatmap_pivot.reindex(columns=month_order)

        fig_heat = go.Figure(
            go.Heatmap(
                z=heatmap_pivot.values,
                x=heatmap_pivot.columns.tolist(),
                y=heatmap_pivot.index.tolist(),
                colorscale=[[0, "#0d9488"], [0.4, "#fbbf24"], [1, "#ef4444"]],
                colorbar=dict(title="Delay %", thickness=10),
                text=heatmap_pivot.values,
                texttemplate="%{text:.0f}%",
                textfont=dict(size=10),
                hovertemplate="<b>%{y}</b> — %{x}<br>Delay Rate: <b>%{z:.1f}%</b><extra></extra>",
            )
        )
        apply_layout(fig_heat, title="Delay Rate: Ship Mode × Month", height=380)
        st.plotly_chart(fig_heat, use_container_width=True)

    with trend_col2:
        # ── Quarter-over-quarter efficiency ──
        st.markdown('<div class="section-header"><h3>Quarterly Efficiency Comparison</h3></div>', unsafe_allow_html=True)

        q_stats = (
            df.groupby(["Order Year", "Order Quarter"])
            .agg(
                Avg_Efficiency=("Route Efficiency Score", "mean"),
                Orders=("Row ID", "count"),
                On_Time_Pct=("Delay Flag", lambda x: (1 - x.mean()) * 100),
            )
            .reset_index()
        )
        q_stats["Quarter_Label"] = q_stats["Order Year"].astype(str) + " Q" + q_stats["Order Quarter"].astype(str)

        fig_qoq = px.bar(
            q_stats,
            x="Quarter_Label",
            y="Avg_Efficiency",
            color="Avg_Efficiency",
            color_continuous_scale=[[0, CORAL], [0.5, AMBER], [1, TEAL]],
            text="Avg_Efficiency",
            custom_data=["Orders", "On_Time_Pct"],
        )
        fig_qoq.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Efficiency: <b>%{y:.2f}</b><br>"
                "Orders: <b>%{customdata[0]:,}</b><br>"
                "On-Time: <b>%{customdata[1]:.1f}%</b>"
                "<extra></extra>"
            ),
        )
        apply_layout(fig_qoq, title="Avg Efficiency Score by Quarter", height=380,
                     showlegend=False, coloraxis_showscale=False)
        fig_qoq.update_xaxes(tickangle=45)
        st.plotly_chart(fig_qoq, use_container_width=True)

    # ── Rolling average lead-time trend ──
    st.markdown('<div class="section-header"><h3>Rolling 30-Day Average Lead Time</h3></div>', unsafe_allow_html=True)

    daily_avg = (
        df.groupby(df["Order Date"].dt.date)
        .agg(Avg_Days=("Shipping Days", "mean"), Orders=("Row ID", "count"))
        .reset_index()
        .sort_values("Order Date")
    )
    daily_avg["Rolling_30"] = daily_avg["Avg_Days"].rolling(window=30, min_periods=5).mean()
    daily_avg["Rolling_90"] = daily_avg["Avg_Days"].rolling(window=90, min_periods=10).mean()

    fig_roll = go.Figure()
    fig_roll.add_trace(
        go.Scatter(
            x=daily_avg["Order Date"],
            y=daily_avg["Avg_Days"],
            mode="markers",
            name="Daily Avg",
            marker=dict(color=TEAL, size=4, opacity=0.3),
            hovertemplate="Date: %{x}<br>Avg Days: %{y:.0f}<extra></extra>",
        )
    )
    fig_roll.add_trace(
        go.Scatter(
            x=daily_avg["Order Date"],
            y=daily_avg["Rolling_30"],
            mode="lines",
            name="30-Day Rolling Avg",
            line=dict(color=AMBER, width=2.5),
            hovertemplate="Date: %{x}<br>30-Day Avg: %{y:.0f}<extra></extra>",
        )
    )
    fig_roll.add_trace(
        go.Scatter(
            x=daily_avg["Order Date"],
            y=daily_avg["Rolling_90"],
            mode="lines",
            name="90-Day Rolling Avg",
            line=dict(color=PURPLE, width=2, dash="dash"),
            hovertemplate="Date: %{x}<br>90-Day Avg: %{y:.0f}<extra></extra>",
        )
    )
    apply_layout(fig_roll, title="Daily Lead Time with Rolling Averages", height=400)
    st.plotly_chart(fig_roll, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 6 — PROFITABILITY & COST ANALYTICS
# ══════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header"><h3>Profit Margin Analysis</h3></div>', unsafe_allow_html=True)

    prof_col1, prof_col2 = st.columns(2)

    with prof_col1:
        # ── Profit margin by region (violin) ──
        fig_viol_r = px.violin(
            df,
            x="Region",
            y="Profit Margin (%)",
            color="Region",
            color_discrete_sequence=[TEAL, AMBER, PURPLE, CORAL, CYAN],
            box=True,
            points="outliers",
        )
        fig_viol_r.update_traces(
            hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>"
        )
        apply_layout(fig_viol_r, title="Profit Margin Distribution by Region", height=440, showlegend=False)
        st.plotly_chart(fig_viol_r, use_container_width=True)

    with prof_col2:
        # ── Profit margin by ship mode (violin) ──
        fig_viol_m = px.violin(
            df,
            x="Ship Mode",
            y="Profit Margin (%)",
            color="Ship Mode",
            color_discrete_sequence=[TEAL, CYAN, AMBER, CORAL],
            box=True,
            points="outliers",
            category_orders={"Ship Mode": ["Same Day", "First Class", "Second Class", "Standard Class"]},
        )
        fig_viol_m.update_traces(
            hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>"
        )
        apply_layout(fig_viol_m, title="Profit Margin Distribution by Ship Mode", height=440, showlegend=False)
        st.plotly_chart(fig_viol_m, use_container_width=True)

    # ── Cost-per-unit vs Shipping Days scatter ──
    st.markdown('<div class="section-header"><h3>Cost Efficiency Frontier</h3></div>', unsafe_allow_html=True)

    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        fig_frontier = px.scatter(
            df,
            x="Shipping Days",
            y="Cost Per Unit",
            color="Ship Mode",
            color_discrete_map={
                "Same Day": PURPLE, "First Class": TEAL,
                "Second Class": AMBER, "Standard Class": CORAL,
            },
            opacity=0.5,
            custom_data=["Region", "Division", "Route Efficiency Score"],
            category_orders={"Ship Mode": ["Same Day", "First Class", "Second Class", "Standard Class"]},
        )
        fig_frontier.update_traces(
            marker=dict(size=5, line=dict(width=0.3, color="#1A1F2E")),
            hovertemplate=(
                "Days: <b>%{x}</b><br>"
                "Cost/Unit: <b>$%{y:.2f}</b><br>"
                "Region: %{customdata[0]}<br>"
                "Division: %{customdata[1]}<br>"
                "Efficiency: %{customdata[2]:.2f}"
                "<extra></extra>"
            ),
        )
        apply_layout(fig_frontier, title="Cost Per Unit vs Shipping Days", height=460)
        st.plotly_chart(fig_frontier, use_container_width=True)

    with cost_col2:
        # ── Revenue Per Unit by Division ──
        div_stats = (
            df.groupby("Division")
            .agg(
                Avg_Revenue_Unit=("Revenue Per Unit", "mean"),
                Avg_Cost_Unit=("Cost Per Unit", "mean"),
                Avg_Margin=("Profit Margin (%)", "mean"),
                Orders=("Row ID", "count"),
            )
            .reset_index()
            .sort_values("Avg_Revenue_Unit", ascending=True)
        )

        fig_div = go.Figure()
        fig_div.add_trace(
            go.Bar(
                y=div_stats["Division"],
                x=div_stats["Avg_Revenue_Unit"],
                name="Revenue / Unit",
                orientation="h",
                marker_color=TEAL,
                text=div_stats["Avg_Revenue_Unit"].round(2),
                texttemplate="$%{text}",
                textposition="outside",
                customdata=div_stats[["Orders", "Avg_Margin"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Revenue/Unit: <b>$%{x:.2f}</b><br>"
                    "Orders: <b>%{customdata[0]:,}</b><br>"
                    "Avg Margin: <b>%{customdata[1]:.1f}%</b>"
                    "<extra></extra>"
                ),
            )
        )
        fig_div.add_trace(
            go.Bar(
                y=div_stats["Division"],
                x=div_stats["Avg_Cost_Unit"],
                name="Cost / Unit",
                orientation="h",
                marker_color=CORAL,
                text=div_stats["Avg_Cost_Unit"].round(2),
                texttemplate="$%{text}",
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Cost/Unit: <b>$%{x:.2f}</b>"
                    "<extra></extra>"
                ),
            )
        )
        apply_layout(fig_div, title="Revenue & Cost Per Unit by Division", height=460, barmode="group")
        fig_div.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_div, use_container_width=True)

    # ── Cost Per Ship Day analysis ──
    st.markdown('<div class="section-header"><h3>Cost Per Ship Day Analysis</h3></div>', unsafe_allow_html=True)

    cpsd_col1, cpsd_col2 = st.columns(2)

    with cpsd_col1:
        # Filter out extreme outliers for better visualization
        cpsd_filtered = df[df["Cost_Per_Ship_Day"] < df["Cost_Per_Ship_Day"].quantile(0.95)].copy()

        cpsd_by_region = (
            cpsd_filtered.groupby("Region")
            .agg(
                Avg_CPSD=("Cost_Per_Ship_Day", "mean"),
                Median_CPSD=("Cost_Per_Ship_Day", "median"),
                Orders=("Row ID", "count"),
            )
            .reset_index()
            .sort_values("Avg_CPSD", ascending=False)
        )

        fig_cpsd = px.bar(
            cpsd_by_region,
            x="Region",
            y=["Avg_CPSD", "Median_CPSD"],
            barmode="group",
            color_discrete_sequence=[TEAL, AMBER],
            labels={"value": "Cost Per Ship Day ($)", "variable": "Metric"},
        )
        fig_cpsd.update_traces(
            hovertemplate="<b>%{x}</b><br>Value: <b>$%{y:.4f}</b><extra></extra>"
        )
        apply_layout(fig_cpsd, title="Avg vs Median Cost/Ship Day by Region", height=400)
        st.plotly_chart(fig_cpsd, use_container_width=True)

    with cpsd_col2:
        # ── Sales per ship day by mode ──
        spsd_by_mode = (
            df.groupby("Ship Mode")
            .agg(
                Avg_Sales_PSD=("Sales_Per_Ship_Day", "mean"),
                Avg_Profit_PSD=("Profit_Per_Ship_Day", "mean"),
                Orders=("Row ID", "count"),
            )
            .reset_index()
        )

        fig_spsd = go.Figure()
        fig_spsd.add_trace(
            go.Bar(
                x=spsd_by_mode["Ship Mode"],
                y=spsd_by_mode["Avg_Sales_PSD"],
                name="Sales / Ship Day",
                marker_color=TEAL,
                text=spsd_by_mode["Avg_Sales_PSD"].round(4),
                texttemplate="$%{text}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Sales/Day: <b>$%{y:.4f}</b><extra></extra>",
            )
        )
        fig_spsd.add_trace(
            go.Bar(
                x=spsd_by_mode["Ship Mode"],
                y=spsd_by_mode["Avg_Profit_PSD"],
                name="Profit / Ship Day",
                marker_color=PURPLE,
                text=spsd_by_mode["Avg_Profit_PSD"].round(4),
                texttemplate="$%{text}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Profit/Day: <b>$%{y:.4f}</b><extra></extra>",
            )
        )
        apply_layout(fig_spsd, title="Avg Sales & Profit Per Ship Day by Mode", height=400, barmode="group")
        st.plotly_chart(fig_spsd, use_container_width=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; padding: 12px 0 24px 0;">
        <span style="color:#4b5563; font-size:0.82rem;">
            Nassau Candy &middot; Shipping Route Efficiency Dashboard &nbsp;&middot;&nbsp; Built with Streamlit &amp; Plotly
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
