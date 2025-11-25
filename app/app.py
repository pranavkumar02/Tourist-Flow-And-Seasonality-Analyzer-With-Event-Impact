import math
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from src.db import get_engine  
from dotenv import load_dotenv

# =========================
#  APP SETUP
# =========================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True,
)
app.title = "Tourist Flow & Seasonality Analyzer"

MAP_H     = "48vh"
KPI_H     = "48vh"
CHART_H   = "26vh"

COLOR_MAP = {
    "Hotspot": "#ef4444",
    "Normal": "#60a5fa",
    "Off-Season": "#f59e0b",
}
CATEGORY_ORDER = {"lift": ["Hotspot", "Normal", "Off-Season"]}

MAP_BG   = "#223542"
CORAL    = "#F88379"
BUBBLE   = "#2aa7d6"

# =========================
#  GLOBAL HTML / CSS (THEME)
# =========================
app.index_string = """
<!DOCTYPE html>
<html>
  <head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
    :root{
        --bg1:#050716;
        --bg2:#0b0f1c;
        --card:#050811;
        --card2:#080d19;
        --border:rgba(148,163,253,.55);
        --glow:rgba(56,189,248,.22);
        --text:#f7f7ff;
        --muted:#9fb3d9;
        --grid:rgba(234,242,246,.06);
        --accent:#a855f7;
    }

    *{
        box-sizing:border-box;
    }

    body, html{
        height:100%;
        margin:0;
        padding:0;
        overflow:hidden;
        background:
            radial-gradient(900px 500px at 15% 0%, rgba(94,234,212,.12), transparent 65%),
            radial-gradient(900px 600px at 85% 0%, rgba(129,140,248,.15), transparent 65%),
            linear-gradient(160deg, var(--bg1), var(--bg2));
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color:var(--text);
    }

    .layout-root{
        display:flex;
        height:100vh;
        width:100vw;
    }

    /* ---- SIDEBAR ---- */
    .sidebar {
        width:230px;
        height:100vh;
        background:linear-gradient(180deg,#050814,#050812);
        padding:24px 18px 18px;
        border-right:1px solid rgba(255,255,255,.06);
        display:flex;
        flex-direction:column;
        gap:22px;
    }

    .sidebar-logo{
        font-weight:800;
        font-size:22px;
        letter-spacing:.18em;
        text-transform:uppercase;
        color:#e5e7ff;
    }

    .sidebar-subtitle{
        font-size:13px;
        color:var(--muted);
        line-height:1.4;
    }

    .sidebar-nav .nav-link{
        border-radius:12px;
        margin-bottom:8px;
        padding:9px 11px;
        font-size:14px;
        color:#c7d2fe;
        display:flex;
        align-items:center;
        gap:8px;
        border:1px solid transparent;
        transition:.2s;
    }

    .sidebar-nav .nav-link .dot{
        width:7px;
        height:7px;
        border-radius:999px;
        background:rgba(148,163,184,.65);
    }

    .sidebar-nav .nav-link:hover{
        background:rgba(148,163,253,.12);
        border-color:rgba(148,163,253,.28);
    }

    .sidebar-nav .nav-link.active{
        background:linear-gradient(135deg,#6366f1,#a855f7);
        color:white;
        border-color:transparent;
        box-shadow:0 0 18px rgba(129,140,248,.55);
    }

    .sidebar-nav .nav-link.active .dot{
        background:white;
    }

    .sidebar-footer{
        margin-top:auto;
        font-size:11px;
        color:var(--muted);
        opacity:.8;
    }

    /* ---- MAIN CONTENT ---- */
    .content-wrapper{
        flex:1;
        padding:18px 22px 14px;
        overflow:hidden;
        display:flex;
        flex-direction:column;
    }

    .page-body{
        height:100%;
        display:flex;
        flex-direction:column;
        gap:16px;
    }

    .header-card{
        background:radial-gradient(circle at top left, rgba(129,140,248,.35), transparent 65%),
                   radial-gradient(circle at bottom right, rgba(45,212,191,.2), transparent 60%),
                   linear-gradient(135deg,rgba(8,11,24,.96),rgba(9,13,28,.94));
        border-radius:20px;
        padding:14px 18px;
        border:1px solid rgba(148,163,253,.7);
        box-shadow:0 0 35px rgba(56,189,248,.35);
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:18px;
    }

    .page-title{
        font-size:24px;
        font-weight:700;
        letter-spacing:.06em;
        text-transform:uppercase;
        color:#ffffff;
    }

    .page-subtitle{
        font-size:13px;
        color:var(--muted);
        margin-top:4px;
        max-width:420px;
    }

    .badge-chip{
        font-size:12px;
        padding:5px 14px;
        border-radius:999px;
        background:rgba(5,10,24,.9);
        border:1px solid rgba(148,163,253,.5);
        display:inline-flex;
        align-items:center;
        gap:6px;
        box-shadow:0 0 18px rgba(56,189,248,.45);
    }

    .badge-dot{
        width:7px;
        height:7px;
        border-radius:999px;
        background:#22c55e;
        box-shadow:0 0 12px rgba(34,197,94,.8);
    }

    /* ---- CARDS ---- */
    .soft-card{
        /* slightly lighter than before */
        background:linear-gradient(180deg,#070b18,#050811);
        border-radius:18px;
        border:1px solid var(--border);
        box-shadow:
            0 0 18px var(--glow),
            inset 0 1px 0 rgba(255,255,255,.04);
        padding:12px 14px;
    }

    .filters-card{
        display:flex;
        flex-direction:column;
        gap:8px;
        margin-top:4px;
    }

    .filters-title{
        font-size:12px;
        text-transform:uppercase;
        letter-spacing:.18em;
        color:#ffffff;
    }

    .filters-row{
        display:grid;
        grid-template-columns:repeat(5, minmax(0, 1fr));
        gap:12px;
    }

    .filter-label{
        font-size:11px;
        color:#ffffff;
        margin-bottom:4px;
        letter-spacing:.04em;
        text-transform:uppercase;
    }

    /* Dropdown styling */
    .dash-dropdown .Select-control{
        background:rgba(5,10,24,.98) !important;
        border:1px solid var(--border) !important;
        border-radius:11px !important;
        min-height:34px;
        font-size:13px;
        color:#ffffff !important;
    }
    .dash-dropdown .Select-value-label{
        color:#ffffff !important;
    }
    .dash-dropdown .Select-placeholder{
        color:#e5e7ff !important;
    }
    .dash-dropdown .Select-menu-outer{
        background:rgba(5,10,24,.98) !important;
        border:1px solid rgba(148,163,253,.35) !important;
        color:#ffffff !important;
        z-index:9999;
    }
    .dash-dropdown .Select-option{
        color:#ffffff !important;
    }

    .main-row{
        display:grid;
        grid-template-columns: minmax(0, 1.5fr) minmax(0, 1.7fr);
        gap:20px;
        min-height:0;
        align-items:stretch;
    }

    .map-card{
        height:48vh;
    }

    .map-side-wrapper{
        display:flex;
        flex-direction:column;
        gap:12px;
        height:48vh;
    }

    .extra-map-kpi-row{
        display:grid;
        grid-template-columns:repeat(2, minmax(0, 1fr));
        gap:12px;
    }

    .kpi-panel{
        display:flex;
        flex-direction:column;
    }

    .kpi-row{
        /* 2 mini-cards per row, 3 rows */
        display:grid;
        grid-template-columns:repeat(2, minmax(0, 1fr));
        gap:10px;
        margin-top:6px;
    }

    .kpi-title{
        font-size:11px;
        color:#ffffff;
        text-transform:uppercase;
        letter-spacing:.11em;
        margin-bottom:3px;
    }

    .kpi-value{
        font-size:20px;
        font-weight:600;
        line-height:1.3;
        color:#ffffff;
    }

    .kpi-card-inner{
        padding:10px 12px;
        border-radius:14px;
        background:linear-gradient(180deg,#080f24,#050b15);
        border:1px solid var(--border);
        box-shadow:
            0 0 18px var(--glow),
            inset 0 1px 0 rgba(255,255,255,.04);
        min-height:70px; /* make all mini cards equal height */
    }

    .charts-grid{
        display:grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap:14px;
        min-height:0;
    }

    .chart-card{
        height:26vh;
        display:flex;
        flex-direction:column;
    }

    .chart-title{
        font-size:11px;
        color:#ffffff;
        text-transform:uppercase;
        letter-spacing:.11em;
        margin-bottom:4px;
    }

    .js-plotly-plot .plotly, .main-svg{
        font-family:"Inter", system-ui, sans-serif !important;
    }

    </style>
  </head>
  <body>
    {%app_entry%}
    <footer>
      {%config%}
      {%scripts%}
      {%renderer%}
    </footer>
  </body>
</html>
"""

# =========================
#  DATA LOADING (CSV)
# =========================
np.random.seed(7)

state_codes = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY",
    "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND",
    "OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
]
state_names = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
    "Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky",
    "Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi",
    "Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico",
    "New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
    "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
    "Virginia","Washington","West Virginia","Wisconsin","Wyoming","District of Columbia"
]
STATE_NAME_MAP = dict(zip(state_codes, state_names))

REGIONS = {
    "East Coast": ["ME","NH","MA","RI","CT","NY","NJ","PA","DE","MD","DC","VA","NC","SC","GA","FL"],
    "West": ["CA","OR","WA","AK","HI"],
    "South": ["TX","OK","AR","LA","MS","AL","TN","KY","GA","FL","SC","NC","VA","WV","MD","DC","DE"],
    "Mountain": ["AZ","NM","CO","UT","NV","ID","MT","WY"],
}
ALL_MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


load_dotenv()  # optional here, but safe. db.py already calls it too.

# =========================
#  DATA LOADING FROM RDS
# =========================
engine = get_engine()

with engine.connect() as conn:
    parks_df = pd.read_sql("""
        SELECT
            state         AS "State",
            park          AS "Park",
            month         AS "Month",
            year          AS "Year",
            recreation_visits AS "Recreation Visits",
            COALESCE(park_type, 'Unknown') AS "Park Type"
        FROM mv_state_month_visits;
    """, conn)

parks_df = parks_df.dropna(subset=["State", "Park", "Month", "Year", "Recreation Visits"])
parks_df["State"] = parks_df["State"].astype(str).str.strip()
parks_df["Park"] = parks_df["Park"].astype(str).str.strip()
parks_df["Month"] = parks_df["Month"].astype(int)
parks_df["Year"] = parks_df["Year"].astype(int)
parks_df["Recreation Visits"] = parks_df["Recreation Visits"].astype(float)

def map_region_group(state_code: str) -> str:
    for r, lst in REGIONS.items():
        if state_code in lst:
            return r
    return "Other"

parks_df["RegionGroup"] = parks_df["State"].map(map_region_group)
YEARS = sorted(parks_df["Year"].unique())
LATEST_YEAR = max(YEARS)

# =========================
#  FILTER HELPER
# =========================
def filter_parks(month_val=None, year_val=None, region_val=None,
                 dest_val=None, park_type_val=None):
    df = parks_df.copy()

    if year_val is not None:
        df = df[df["Year"] == int(year_val)]

    if month_val is not None:
        df = df[df["Month"] == int(month_val)]

    if region_val and region_val != "All":
        allowed = set(REGIONS.get(region_val, []))
        df = df[df["State"].isin(allowed)]

    if dest_val == "National Park":
        df = df[df["Park Type"].str.contains("National Park", case=False, na=False)]
    elif dest_val == "City":
        df = df[~df["Park Type"].str.contains("National Park", case=False, na=False)]

    if park_type_val and park_type_val != "All":
        df = df[df["Park Type"] == park_type_val]

    return df

# =========================
#  MAP + FIGURE HELPERS
# =========================
def classify_state_status(month_val, year_val, region_val, dest_val, park_type_val):
    df = filter_parks(month_val, year_val, region_val, dest_val, park_type_val)
    if df.empty:
        return {s: "Normal" for s in state_codes}

    grouped = df.groupby("State", as_index=False)["Recreation Visits"].sum()
    q_off = grouped["Recreation Visits"].quantile(0.33)
    q_hot = grouped["Recreation Visits"].quantile(0.66)

    status = {}
    for _, row in grouped.iterrows():
        v = row["Recreation Visits"]
        if v >= q_hot:
            seg = "Hotspot"
        elif v <= q_off:
            seg = "Off-Season"
        else:
            seg = "Normal"
        status[row["State"]] = seg

    for s in state_codes:
        status.setdefault(s, "Normal")

    return status

def build_base_map_df(month_val, year_val, region_val, dest_val, park_type_val):
    status_map = classify_state_status(month_val, year_val, region_val, dest_val, park_type_val)

    df = pd.DataFrame({
        "state": state_codes,
        "state_name": [STATE_NAME_MAP[s] for s in state_codes],
        "lift": [status_map[s] for s in state_codes],
    })
    df["lift"] = pd.Categorical(df["lift"],
                                categories=CATEGORY_ORDER["lift"],
                                ordered=True)

    df_month = filter_parks(month_val, year_val, region_val, dest_val, park_type_val)
    if df_month.empty:
        df["hover_parks"] = "No park data"
        return df

    grouped = df_month.groupby(["State", "Park"], as_index=False)["Recreation Visits"].sum()
    top_by_state = (
        grouped.sort_values("Recreation Visits", ascending=False)
        .groupby("State")["Park"]
        .apply(list)
        .to_dict()
    )

    hover = []
    for _, row in df.iterrows():
        parks = top_by_state.get(row["state"], [])
        if not parks:
            hover.append("No park data")
        else:
            hover.append(", ".join(parks[:5]))
    df["hover_parks"] = hover
    return df

def _common_layout(fig):
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
    )
    fig.update_xaxes(gridcolor="var(--grid)", zeroline=False, showline=False)
    fig.update_yaxes(gridcolor="var(--grid)", zeroline=False, showline=False)
    return fig

def build_map(df):
    fig = px.choropleth(
        df,
        locations="state",
        locationmode="USA-states",
        color="lift",
        custom_data=["lift", "state_name", "hover_parks"],
        color_discrete_map=COLOR_MAP,
        category_orders=CATEGORY_ORDER,
        scope="usa",
        hover_name="state_name",
        hover_data={"state": False, "state_name": False,
                    "lift": True, "hover_parks": False},
        labels={"lift": "Status"},
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            showlakes=False,
            showland=True,
            landcolor="#050811",
        ),
        legend=dict(
            title="Status",
            orientation="v",
            y=0.98,
            yanchor="top",
            x=0.98,
            xanchor="right",
            bgcolor="rgba(5,10,24,.9)",
            font=dict(color="#ffffff"),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        hoverlabel=dict(
            bgcolor="rgba(5,10,24,.95)",
            font_color="#ffffff",
        ),
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[1]}</b>"
            "<br>Status: %{customdata[0]}"
            "<br>Top parks: %{customdata[2]}<extra></extra>"
        )
    )

    return fig

def build_heatmap_real(region_val, dest_val, year_val, park_type_val):
    df = filter_parks(None, year_val, region_val, dest_val, park_type_val)
    if df.empty:
        order_regions = ["East Coast", "Mountain", "South", "West"]
        seasons = ["Spring", "Summer", "Fall", "Winter"]
        pivot = pd.DataFrame(0, index=order_regions, columns=seasons)
    else:
        def month_to_season(m):
            if m in [3, 4, 5]:
                return "Spring"
            if m in [6, 7, 8]:
                return "Summer"
            if m in [9, 10, 11]:
                return "Fall"
            return "Winter"

        df["Season"] = df["Month"].apply(month_to_season)
        agg = df.groupby(["RegionGroup", "Season"], as_index=False)["Recreation Visits"].sum()
        agg = agg[agg["RegionGroup"] != "Other"]
        order_regions = ["East Coast", "Mountain", "South", "West"]
        seasons = ["Spring", "Summer", "Fall", "Winter"]
        pivot = (
            agg.pivot(index="RegionGroup", columns="Season", values="Recreation Visits")
            .reindex(index=order_regions, columns=seasons)
            .fillna(0.0)
        )

    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(color="Visits"),
        text_auto=False,
    )
    fig = _common_layout(fig)
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Visits",
        )
    )
    fig.update_xaxes(title="", type="category")
    fig.update_yaxes(title="", type="category")
    return fig

def build_trend_real(year_val, region_val, dest_val, park_type_val):
    df = filter_parks(None, year_val, region_val, dest_val, park_type_val)
    if df.empty:
        visits = np.zeros(12)
    else:
        agg = df.groupby("Month", as_index=False)["Recreation Visits"].sum().set_index("Month")
        visits = [agg["Recreation Visits"].get(m, 0.0) for m in range(1, 13)]

    dfl = pd.DataFrame({"MonthName": ALL_MONTHS, "Visits": visits})
    fig = px.line(dfl, x="MonthName", y="Visits", markers=True)
    fig = _common_layout(fig)
    fig.update_traces(line=dict(width=2))
    fig.update_traces(line_color="#27a4d8")  # unify line color
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="Tourist inflow", showgrid=False)
    return fig

def build_top5_parks(year_val, region_val, dest_val, park_type_val):
    df = filter_parks(None, year_val, region_val, dest_val, park_type_val)
    if df.empty:
        parks = pd.DataFrame({"Park": ["—"], "Recreation Visits": [0.0], "short": ["—"], "State": ["—"]})
    else:
        agg = (
            df.groupby(["State", "Park"], as_index=False)["Recreation Visits"]
              .sum()
              .sort_values("Recreation Visits", ascending=False)
              .head(5)
        )
        agg["short"] = agg["State"]
        parks = agg

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=parks["Recreation Visits"],
            y=parks["short"],
            orientation="h",
            marker=dict(color=CORAL),
            customdata=parks["Park"],
            hovertemplate="<b>%{customdata}</b><br>Visits: %{x:,.0f}<extra></extra>",
            showlegend=False,
        )
    )
    fig = _common_layout(fig)
    fig.update_xaxes(title="Visits", showgrid=True, gridcolor="rgba(255,255,255,.08)")
    fig.update_yaxes(title="State", showgrid=False)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        hoverlabel=dict(bgcolor="rgba(5,10,24,.95)", font_color="#ffffff"),
    )
    return fig

def build_yearly_trend(region_val, dest_val, park_type_val):
    df = filter_parks(None, None, region_val, dest_val, park_type_val)
    if df.empty:
        yearly = pd.DataFrame({"Year": [0], "Recreation Visits": [0.0]})
    else:
        yearly = (
            df.groupby("Year", as_index=False)["Recreation Visits"]
              .sum()
              .sort_values("Year")
        )

    fig = px.line(yearly, x="Year", y="Recreation Visits", markers=True)
    fig = _common_layout(fig)
    fig.update_traces(line=dict(width=2), line_color="#27a4d8")
    fig.update_xaxes(title="Year", showgrid=False)
    fig.update_yaxes(title="Visits", showgrid=True, gridcolor="rgba(255,255,255,.08)")
    return fig

# ---- NEW: TOP PARK PER YEAR (AREA CHART) ----
def build_top_park_area(region_val, dest_val, park_type_val):
    df = filter_parks(None, None, region_val, dest_val, park_type_val)
    if df.empty:
        yearly_top = pd.DataFrame({"Year": [0], "Visits": [0.0]})
    else:
        # total visits per park per year
        yearly = (
            df.groupby(["Year", "Park"], as_index=False)["Recreation Visits"]
              .sum()
        )
        # for each year pick the park with max visits
        idx = yearly.groupby("Year")["Recreation Visits"].idxmax()
        yearly_top = yearly.loc[idx, ["Year", "Recreation Visits"]].rename(
            columns={"Recreation Visits": "Visits"}
        ).sort_values("Year")

    fig = px.area(
        yearly_top,
        x="Year",
        y="Visits",
    )
    fig = _common_layout(fig)
    fig.update_traces(
        line=dict(width=2, color="#27a4d8"),
        fill="tozeroy",
        fillcolor="rgba(39,164,216,0.45)"
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="Visits", showgrid=True, gridcolor="rgba(255,255,255,.12)")
    return fig

# ---- NEW: BUBBLE CHART (TOP PARKS, YEAR) ----
def build_bubble_chart(year_val, region_val, dest_val, park_type_val):
    df = filter_parks(None, year_val, region_val, dest_val, park_type_val)
    if df.empty:
        return _common_layout(go.Figure())

    # aggregate by park for that year
    agg = (
        df.groupby(["State", "Park"], as_index=False)["Recreation Visits"]
          .sum()
          .sort_values("Recreation Visits", ascending=False)
          .head(40)  # many points → more colourful
    )
    agg["StateName"] = agg["State"].map(STATE_NAME_MAP)

    fig = px.scatter(
        agg,
        x="StateName",
        y="Recreation Visits",
        size="Recreation Visits",
        color="StateName",
        hover_name="Park",
        size_max=40,
    )
    fig = _common_layout(fig)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="Visits", showgrid=True, gridcolor="rgba(255,255,255,.12)")
    return fig

# =========================
#  KPI HELPERS
# =========================
def fmt_millions(val: float) -> str:
    if val >= 1e9:
        return f"{val/1e9:.1f}B"
    if val >= 1e6:
        return f"{val/1e6:.1f}M"
    if val >= 1e3:
        return f"{val/1e3:.1f}K"
    return f"{val:.0f}"

def compute_kpis(month_val, year_val, region_val, dest_val, park_type_val):
    month_int = int(month_val)
    year_int  = int(year_val)

    df_month = filter_parks(month_int, year_int, region_val, dest_val, park_type_val)
    if df_month.empty:
        top_park_month = "—"
        total_month = 0.0
        avg = 0.0
    else:
        g = (
            df_month.groupby("Park")["Recreation Visits"]
                    .sum()
                    .sort_values(ascending=False)
        )
        top_park_month = g.index[0]
        total_month = float(g.sum())
        avg = total_month / max(g.size, 1)

    df_all = filter_parks(None, None, region_val, dest_val, park_type_val)
    if df_all.empty:
        peak_year = year_int
        yoy_pct = 0.0
    else:
        yearly = df_all.groupby("Year", as_index=False)["Recreation Visits"].sum()
        peak_row = yearly.sort_values("Recreation Visits", ascending=False).iloc[0]
        peak_year = int(peak_row["Year"])
        curr = yearly[yearly["Year"] == year_int]["Recreation Visits"]
        prev = yearly[yearly["Year"] == (year_int - 1)]["Recreation Visits"]
        if curr.empty or prev.empty or prev.iloc[0] == 0:
            yoy_pct = 0.0
        else:
            yoy_pct = (curr.iloc[0] - prev.iloc[0]) / prev.iloc[0] * 100.0

    df_year = filter_parks(None, year_int, region_val, dest_val, park_type_val)
    if df_year.empty:
        top_park_year = "—"
        total_year = 0.0
        top_state_year = "—"
    else:
        g_year = (
            df_year.groupby("Park")["Recreation Visits"]
                   .sum()
                   .sort_values(ascending=False)
        )
        top_park_year = g_year.index[0]

        total_year = float(df_year["Recreation Visits"].sum())
        state_year = (
            df_year.groupby("State")["Recreation Visits"]
                  .sum()
                  .sort_values(ascending=False)
        )
        if len(state_year) == 0:
            top_state_year = "—"
        else:
            top_state_code = state_year.index[0]
            top_state_year = STATE_NAME_MAP.get(top_state_code, top_state_code)

    return {
        "top_park_month": top_park_month,
        "avg_per_park": avg,
        "total_month": total_month,
        "peak_year": peak_year,
        "yoy_pct": yoy_pct,
        "yoy_positive": yoy_pct >= 0,
        "top_park_year": top_park_year,
        "total_year": total_year,
        "top_state_year": top_state_year,
    }

# ---- QUICK INSIGHTS (TEXT) ----
def compute_quick_insights(month_val, year_val, region_val, dest_val, park_type_val):
    df = filter_parks(month_val, year_val, region_val, dest_val, park_type_val)

    if df.empty:
        return [
            "No data available for selected filters.",
            "",
            ""
        ]

    # 1 — Top State This Month
    state_sum = df.groupby("State")["Recreation Visits"].sum()
    top_state = state_sum.idxmax()
    top_state_name = STATE_NAME_MAP.get(top_state, top_state)
    top_visits = state_sum.max()
    line1 = f"{top_state_name} leads this month with {fmt_millions(top_visits)} visitors."

    # 2 — Seasonality Split (within selected year)
    def month_to_season(m):
        if m in [3, 4, 5]:
            return "Spring"
        if m in [6, 7, 8]:
            return "Summer"
        if m in [9, 10, 11]:
            return "Fall"
        return "Winter"

    df["Season"] = df["Month"].apply(month_to_season)
    season_pct = (
        df.groupby("Season")["Recreation Visits"]
          .sum()
          .pipe(lambda s: s / s.sum() * 100)
    )
    top_season = season_pct.idxmax()
    top_season_val = season_pct.max()
    line2 = f"{top_season} accounts for {top_season_val:.1f}% of visits under current filters."

    # 3 — YoY Growth Summary (reuse KPI logic)
    k = compute_kpis(month_val, year_val, region_val, dest_val, park_type_val)
    yoy_pct = k["yoy_pct"]
    yoy_word = "growth" if yoy_pct >= 0 else "decline"
    line3 = f"Year-on-year {yoy_word} vs previous year is {yoy_pct:+.1f}%."

    return [line1, line2, line3]

# =========================
#  INITIAL FIGURES
# =========================
DEFAULT_MONTH = 7
DEFAULT_YEAR = LATEST_YEAR

df_map_init  = build_base_map_df(DEFAULT_MONTH, DEFAULT_YEAR, "All", "State", "All")
init_map     = build_map(df_map_init)
init_heat    = build_heatmap_real("All", "State", DEFAULT_YEAR, "All")
init_trend   = build_trend_real(DEFAULT_YEAR, "All", "State", "All")
init_top5    = build_top5_parks(DEFAULT_YEAR, "All", "State", "All")
init_yearly  = build_yearly_trend("All", "State", "All")
init_top_area = build_top_park_area("All", "State", "All")
init_bubble  = build_bubble_chart(DEFAULT_YEAR, "All", "State", "All")
kpi0         = compute_kpis(DEFAULT_MONTH, DEFAULT_YEAR, "All", "State", "All")

# =========================
#  COMPONENTS (CARDS)
# =========================
def filter_dropdowns_card():
    return dbc.Card(
        [
            html.Div("Filters", className="filters-title"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Month", className="filter-label"),
                            dcc.Dropdown(
                                id="f-month",
                                className="dash-dropdown",
                                options=[
                                    {"label": m, "value": i + 1}
                                    for i, m in enumerate(
                                        [
                                            "January","February","March","April","May","June",
                                            "July","August","September","October","November","December"
                                        ]
                                    )
                                ],
                                value=DEFAULT_MONTH,
                                clearable=False,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div("Year", className="filter-label"),
                            dcc.Dropdown(
                                id="f-year",
                                className="dash-dropdown",
                                options=[{"label": str(y), "value": int(y)} for y in YEARS],
                                value=DEFAULT_YEAR,
                                clearable=False,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div("Region", className="filter-label"),
                            dcc.Dropdown(
                                id="f-region",
                                className="dash-dropdown",
                                options=[
                                    {"label": r, "value": r}
                                    for r in ["All","East Coast","West","South","Mountain"]
                                ],
                                value="All",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div("Destination Type", className="filter-label"),
                            dcc.Dropdown(
                                id="f-dest",
                                className="dash-dropdown",
                                options=[
                                    {"label": x, "value": x}
                                    for x in ["State","City","National Park"]
                                ],
                                value="State",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div("Park Type", className="filter-label"),
                            dcc.Dropdown(
                                id="f-park-type",
                                className="dash-dropdown",
                                options=(
                                    [{"label": "All", "value": "All"}] +
                                    [
                                        {"label": t, "value": t}
                                        for t in sorted(parks_df["Park Type"].dropna().unique())
                                    ]
                                ),
                                value="All",
                                clearable=False,
                            ),
                        ]
                    ),
                ],
                className="filters-row",
            ),
        ],
        className="soft-card filters-card",
    )

def kpi_card(title, idv):
    return html.Div(
        dbc.Card(
            [
                html.Div(title, className="kpi-title"),
                html.Div(id=idv, children="—", className="kpi-value"),
            ],
            className="kpi-card-inner",
        )
    )

def extra_kpi_card(title, idv):
    return html.Div(
        dbc.Card(
            [
                html.Div(title, className="kpi-title"),
                html.Div(id=idv, children="—", className="kpi-value"),
            ],
            className="kpi-card-inner",
        )
    )

# LEFT COLUMN: key signals + key findings text
kpi_panel = dbc.Card(
    [
        html.Div("Key Signals", className="kpi-title"),
        html.Div(
            [
                kpi_card("Top Park (Month)", "kpi-top-park-month"),
                kpi_card("Avg Visits / Park", "kpi-avg-park"),
                kpi_card("Total Visitors (Month)", "kpi-total-month"),
                kpi_card("Peak Year", "kpi-peak-year"),
                kpi_card("YoY Growth vs Prev Year", "kpi-yoy"),
                kpi_card("Top Park (Year)", "kpi-top-park-year"),
            ],
            className="kpi-row",
        ),
        html.Div(
            [
                html.Div("Key Findings", className="kpi-title", style={"marginTop": "10px"}),
                html.Div(id="quick-insights-line1", className="kpi-value", style={"fontSize": "15px"}),
                html.Div(id="quick-insights-line2", className="kpi-value", style={"fontSize": "15px"}),
                html.Div(id="quick-insights-line3", className="kpi-value", style={"fontSize": "15px"}),
            ]
        ),
    ],
    className="soft-card kpi-panel",
)

map_card = dbc.Card(
    dcc.Graph(
        id="us-map",
        figure=init_map,
        style={"height": "100%", "backgroundColor": "transparent"},
        config={"displayModeBar": False},
    ),
    className="soft-card map-card",
)

# Analytics charts
heat_card = dbc.Card(
    [
        html.Div("Region–Season Heat", className="chart-title"),
        dcc.Graph(
            id="heatmap-analytics",
            figure=init_heat,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card chart-card",
)

trend_card = dbc.Card(
    [
        html.Div("Monthly Trend", className="chart-title"),
        dcc.Graph(
            id="trend-analytics",
            figure=init_trend,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card chart-card",
)

top5_parks_card = dbc.Card(
    [
        html.Div("Top 5 Parks", className="chart-title"),
        dcc.Graph(
            id="top5-parks-analytics",
            figure=init_top5,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card chart-card",
)

top_area_card = dbc.Card(
    [
        html.Div("Top Park per Year (Area)", className="chart-title"),
        dcc.Graph(
            id="top-park-area-analytics",
            figure=init_top_area,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card chart-card",
)

yearly_card = dbc.Card(
    [
        html.Div("Yearly Visitors Trend", className="chart-title"),
        dcc.Graph(
            id="yearly-analytics",
            figure=init_yearly,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card chart-card",
)

bubble_card = dbc.Card(
    [
        html.Div("Top Parks Bubble (Year)", className="chart-title"),
        dcc.Graph(
            id="bubble-analytics",
            figure=init_bubble,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card chart-card",
)

# =========================
#  PAGE LAYOUTS
# =========================
def dashboard_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Tourist Flow & Seasonality Analyzer",
                                     className="page-title"),
                            html.Div(
                                "Explore how national parks and destinations move between hotspot, normal and off-season across the U.S.",
                                className="page-subtitle",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(className="badge-dot"),
                                    html.Span("Live Exploration", style={"fontWeight": 500}),
                                ],
                                className="badge-chip",
                            )
                        ]
                    ),
                ],
                className="header-card",
            ),

            filter_dropdowns_card(),

            html.Div(
                [
                    html.Div(kpi_panel),

                    html.Div(
                        [
                            map_card,
                            html.Div(
                                [
                                    extra_kpi_card("Total Visitors (Year)", "kpi-total-year"),
                                    extra_kpi_card("Most Visited State (Year)", "kpi-top-state-year"),
                                ],
                                className="extra-map-kpi-row",
                            ),
                        ],
                        className="map-side-wrapper",
                    ),
                ],
                className="main-row",
            ),
        ],
        className="page-body",
    )

def analytics_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Analytics Deep Dive",
                                     className="page-title"),
                            html.Div(
                                "Seasonality patterns, yearly movement and state-level leaders driven by your filters.",
                                className="page-subtitle",
                            ),
                        ]
                    ),
                ],
                className="header-card",
            ),

            filter_dropdowns_card(),

            html.Div(
                [
                    heat_card,
                    trend_card,
                    top5_parks_card,
                    top_area_card,   # area chart instead of top 10 states
                    yearly_card,
                    bubble_card,     # bubble chart instead of park-type bar
                ],
                className="charts-grid",
            ),
        ],
        className="page-body",
    )

def reports_layout():
    return dbc.Container(
        dbc.Card(
            [
                html.H3("Reports", className="kpi-title mb-2"),
                html.P(
                    "Reserved for PDF exports, narrative summaries, and stakeholder-ready reports.",
                    style={"fontSize": "14px"},
                ),
            ],
            className="soft-card",
            style={"marginTop": "16px"},
        ),
        fluid=True,
        className="dbc-container pb-2",
        style={"height": "100vh", "overflow": "hidden"},
    )

def settings_layout():
    return dbc.Container(
        dbc.Card(
            [
                html.H3("Settings", className="kpi-title mb-2"),
                html.P(
                    "Space for theme toggles, default filters and user preferences.",
                    style={"FontSize": "14px"},
                ),
            ],
            className="soft-card",
            style={"marginTop": "16px"},
        ),
        fluid=True,
        className="dbc-container pb-2",
        style={"height": "100vh", "overflow": "hidden"},
    )

# =========================
#  SIDEBAR + MAIN LAYOUT
# =========================
sidebar = html.Div(
    [
        html.Div("TFSA", className="sidebar-logo"),
        html.Div("Tourist Flow & Seasonality", className="sidebar-subtitle"),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.Span(className="dot"), "Dashboard"],
                    href="/",
                    active="exact",
                    className="nav-link",
                ),
                dbc.NavLink(
                    [html.Span(className="dot"), "Analytics"],
                    href="/analytics",
                    active="exact",
                    className="nav-link",
                ),
                dbc.NavLink(
                    [html.Span(className="dot"), "Reports"],
                    href="/reports",
                    active="exact",
                    className="nav-link",
                ),
                dbc.NavLink(
                    [html.Span(className="dot"), "Settings"],
                    href="/settings",
                    active="exact",
                    className="nav-link",
                ),
            ],
            vertical=True,
            pills=True,
            className="sidebar-nav",
        ),
        html.Div(
            "Capstone · National Parks Visitor Insights",
            className="sidebar-footer",
        ),
    ],
    className="sidebar",
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(sidebar, className=""),
        html.Div(id="page-content", className="content-wrapper"),
    ],
    className="layout-root",
)

# =========================
#  PAGE SWITCHING
# =========================
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def render_page(pathname):
    if pathname in ["/", "/dashboard", None]:
        return dashboard_layout()
    if pathname == "/analytics":
        return analytics_layout()
    if pathname == "/reports":
        return reports_layout()
    if pathname == "/settings":
        return settings_layout()
    return dashboard_layout()

# =========================
#  CALLBACKS — MAP
# =========================
@app.callback(
    Output("us-map", "figure"),
    [
        Input("f-month", "value"),
        Input("f-year", "value"),
        Input("f-region", "value"),
        Input("f-dest", "value"),
        Input("f-park-type", "value"),
    ],
)
def update_map(month_val, year_val, region_val, dest_val, park_type_val):
    dfm = build_base_map_df(month_val, year_val, region_val, dest_val, park_type_val)
    return build_map(dfm)

# =========================
#  CALLBACKS — ANALYTICS CHARTS
# =========================
@app.callback(
    [
        Output("heatmap-analytics", "figure"),
        Output("trend-analytics", "figure"),
        Output("top5-parks-analytics", "figure"),
        Output("top-park-area-analytics", "figure"),
        Output("yearly-analytics", "figure"),
        Output("bubble-analytics", "figure"),
    ],
    [
        Input("f-month", "value"),
        Input("f-year", "value"),
        Input("f-region", "value"),
        Input("f-dest", "value"),
        Input("f-park-type", "value"),
    ],
)
def update_analytics_charts(month_val, year_val, region_val, dest_val, park_type_val):
    heat_out   = build_heatmap_real(region_val, dest_val, year_val, park_type_val)
    trend_out  = build_trend_real(year_val, region_val, dest_val, park_type_val)
    top5_out   = build_top5_parks(year_val, region_val, dest_val, park_type_val)
    area_out   = build_top_park_area(region_val, dest_val, park_type_val)
    yearly_out = build_yearly_trend(region_val, dest_val, park_type_val)
    bubble_out = build_bubble_chart(year_val, region_val, dest_val, park_type_val)
    return heat_out, trend_out, top5_out, area_out, yearly_out, bubble_out

# =========================
#  CALLBACKS — KPIs + KEY FINDINGS
# =========================
@app.callback(
    [
        Output("kpi-top-park-month", "children"),
        Output("kpi-avg-park", "children"),
        Output("kpi-total-month", "children"),
        Output("kpi-peak-year", "children"),
        Output("kpi-yoy", "children"),
        Output("kpi-yoy", "style"),
        Output("kpi-top-park-year", "children"),
        Output("kpi-total-year", "children"),
        Output("kpi-top-state-year", "children"),
    ],
    [
        Input("f-month", "value"),
        Input("f-year", "value"),
        Input("f-region", "value"),
        Input("f-dest", "value"),
        Input("f-park-type", "value"),
    ],
)
def update_kpis(month_val, year_val, region_val, dest_val, park_type_val):
    k = compute_kpis(month_val, year_val, region_val, dest_val, park_type_val)
    yoy_text = f"{k['yoy_pct']:+.1f}%"
    yoy_style = {"color": "#4ade80" if k["yoy_positive"] else "#f97373"}
    return (
        k["top_park_month"],
        f"{k['avg_per_park']:,.0f}",
        fmt_millions(k["total_month"]),
        str(k["peak_year"]),
        yoy_text,
        yoy_style,
        k["top_park_year"],
        fmt_millions(k["total_year"]),
        k["top_state_year"],
    )

@app.callback(
    [
        Output("quick-insights-line1", "children"),
        Output("quick-insights-line2", "children"),
        Output("quick-insights-line3", "children"),
    ],
    [
        Input("f-month", "value"),
        Input("f-year", "value"),
        Input("f-region", "value"),
        Input("f-dest", "value"),
        Input("f-park-type", "value"),
    ],
)
def update_key_findings(month_val, year_val, region_val, dest_val, park_type_val):
    lines = compute_quick_insights(month_val, year_val, region_val, dest_val, park_type_val)
    return lines[0], lines[1], lines[2]

# =========================
#  RUN
# =========================
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)