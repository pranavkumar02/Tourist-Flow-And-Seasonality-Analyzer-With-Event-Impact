import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# =========================
#  APP & THEME
# =========================
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True,
)
app.title = "Tourist Flow & Seasonality Analyzer"

# ---- Layout tuning ----
MAP_H     = "50vh"
COLUMN_H  = "51vh"   # reduced from 56vh → FIXES GAP
KPI_H     = "11vh"
CHART_H   = "20vh"
TITLE_TOP = "4px"

COLOR_MAP = {
    "Hotspot": "#ef4444",
    "Normal": "#60a5fa",
    "Off-Season": "#f59e0b",
}
CATEGORY_ORDER = {"lift": ["Hotspot", "Normal", "Off-Season"]}
MAP_BG   = "#223542"
CORAL    = "#F88379"   # Top-5 bar color
BUBBLE   = "#2aa7d6"   # area chart color

# =========================
#  PAGE SHELL / CSS
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
        --bg1:#0e2b34; --bg2:#233b45;
        --panel:#263d49; --panel-2:#223542;
        --border:rgba(255,255,255,.12);
        --shadow-dark:rgba(6,14,18,.65);
        --shadow-light:rgba(255,255,255,.07);
        --glow:rgba(56,189,248,.18);
        --text:#ffffff; --muted:#cfe1ea;
        --grid:rgba(234,242,246,.045);
      }

      @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600;700&display=swap');

      html, body{
        height:100%; margin:0; overflow:hidden;
        background:
          radial-gradient(1100px 540px at 18% 8%, rgba(108,209,255,.08), transparent 60%),
          radial-gradient(900px 420px at 85% 0%, rgba(108,209,255,.06), transparent 55%),
          linear-gradient(135deg, var(--bg1), var(--bg2));
        color:var(--text);
        font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
      }

      .dbc-container{
        background:linear-gradient(180deg, rgba(255,255,255,.02), rgba(0,0,0,.03));
        border-radius:22px;
        box-shadow:
          24px 24px 44px var(--shadow-dark),
          -10px -10px 18px var(--shadow-light),
          inset 0 1px 0 rgba(255,255,255,.06),
          0 0 22px var(--glow);
        padding:10px 12px 12px 12px;
      }

      .soft-card{
        border-radius:18px;
        background:linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
        border:1px solid var(--border);
        box-shadow:
          16px 18px 30px var(--shadow-dark),
          -8px -8px 16px var(--shadow-light),
          inset 0 1px 0 rgba(255,255,255,.04),
          0 0 14px var(--glow);
      }
      .tight{ padding:12px 14px; }

      .map-card{
        background:
          radial-gradient(900px 420px at 50% 28%, #2c4654 0%, var(--panel-2) 70%),
          linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
        box-shadow:
          inset 0 1px 0 rgba(255,255,255,.06),
          16px 18px 30px var(--shadow-dark),
          -8px -8px 16px var(--shadow-light),
          0 0 14px var(--glow);
      }

      .section-title{
        width:100%;
        font-family:"Playfair Display", serif;
        font-size:36px; font-weight:700; letter-spacing:.4px;
        text-align:center;
        background: linear-gradient(180deg,#ffffff,#cfe9ff);
        -webkit-background-clip:text; background-clip:text;
        color:transparent;
        text-shadow:0 2px 3px rgba(0,0,0,.35);
        margin:0;
        transform: translateY(-4px);
      }

      .kpi-title{font-size:12px; color:#ffffff; margin-bottom:6px;}
      .kpi-value{font-weight:700; font-size:22px; margin:0; color:#ffffff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
      .kpi-row{display:flex; gap:12px; width:100%;}
      .kpi-col{flex:1 1 0; max-width:none; display:flex;}
      .kpi-col>.card{width:100%;}

      /* Dropdown styling */
      .dash-dropdown .Select-control, .Select-control{
        background:linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%) !important;
        border:1px solid var(--border) !important;
        border-radius:10px !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,.04) !important;
        color:#ffffff !important;
      }
      .dash-dropdown .Select-value-label,
      .dash-dropdown .Select-placeholder,
      .dash-dropdown .Select-input > input,
      .Select-value-label, .Select-placeholder, .Select-input > input{
        color:#ffffff !important;
      }

      /* MAKE MENU SHORTER & SCROLLABLE */
      .dash-dropdown .Select-menu-outer,
      .Select-menu-outer{
        background:var(--panel) !important;
        border:1px solid var(--border) !important;
        max-height:200px !important;
        overflow-y:auto !important;
        z-index:9999 !important;
      }

      .dash-dropdown .Select-menu-outer .Select-option,
      .Select-menu-outer .Select-option,
      .VirtualizedSelectOption,
      .Select-option{
        color:#ffffff !important; background:transparent !important;
      }
      .dash-dropdown .Select-menu-outer .Select-option.is-focused,
      .Select-menu-outer .Select-option.is-focused,
      .VirtualizedSelectFocusedOption{
        background:rgba(255,255,255,.12) !important; color:#ffffff !important;
      }
      .dash-dropdown .Select-arrow, .dash-dropdown .Select-clear-zone,
      .Select-arrow, .Select-clear-zone{ color:#ffffff !important; fill:#ffffff !important; }

      .js-plotly-plot .plotly, .main-svg{
        font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, sans-serif !important;
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
#  DATA LOADING
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

PARKS_CSV_PATH = Path(__file__).parent / "all_parks_recreation_visits.csv"

parks_df = pd.read_csv(PARKS_CSV_PATH)

parks_df = parks_df.dropna(subset=["State", "Park", "Month", "Year", "Recreation Visits"])
parks_df["State"] = parks_df["State"].astype(str).str.strip()
parks_df["Park"] = parks_df["Park"].astype(str).str.strip()
parks_df["Month"] = parks_df["Month"].astype(int)
parks_df["Year"] = parks_df["Year"].astype(int)
parks_df["Recreation Visits"] = parks_df["Recreation Visits"].astype(float)

if "Park Type" not in parks_df.columns:
    parks_df["Park Type"] = "Unknown"

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

    # Destination type – very simple logic
    if dest_val == "National Park":
        df = df[df["Park Type"].str.contains("National Park", case=False, na=False)]
    elif dest_val == "City":
        df = df[~df["Park Type"].str.contains("National Park", case=False, na=False)]
    # dest_val == "State" → no extra filter

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
        paper_bgcolor=MAP_BG,
        plot_bgcolor=MAP_BG,
        geo=dict(
            bgcolor=MAP_BG,
            showlakes=False,
            showland=True,
            landcolor=MAP_BG,
        ),
        legend=dict(
            title="Status",
            orientation="v",
            y=0.98,
            yanchor="top",
            x=0.98,
            xanchor="right",
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        hoverlabel=dict(bgcolor="rgba(10,20,25,.9)", font_color="#ffffff"),
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
        text_auto=False,  # numbers only in hover
    )
    fig = _common_layout(fig)
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Visits",
            tickfont=dict(color="#ffffff"),
            titlefont=dict(color="#ffffff"),
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
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="Tourist inflows", showgrid=False)
    return fig

def build_top_park_per_year_bubble(region_val, dest_val, park_type_val):
    """
    AREA chart: each point = TOP park of that year.
    x = Year, y = Visits, filled to zero.
    """
    df = filter_parks(None, None, region_val, dest_val, park_type_val)
    if df.empty:
        df_top = pd.DataFrame({"Year": [0], "Park": ["—"], "Recreation Visits": [0.0]})
    else:
        agg = df.groupby(["Year", "Park"], as_index=False)["Recreation Visits"].sum()
        # keep biggest park per year
        top_per_year = (
            agg.sort_values(["Year", "Recreation Visits"], ascending=[True, False])
               .groupby("Year")
               .head(1)
        )
        df_top = top_per_year.sort_values("Year")
        # only last 20 years to keep it readable
        if len(df_top) > 20:
            df_top = df_top.tail(20)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_top["Year"],
            y=df_top["Recreation Visits"],
            mode="lines",
            fill="tozeroy",
            line=dict(color=BUBBLE, width=2),
            hovertext=df_top["Park"],
            hovertemplate="<b>%{hovertext}</b><br>Year: %{x}<br>Visits: %{y:,.0f}<extra></extra>",
        )
    )
    fig = _common_layout(fig)
    fig.update_xaxes(title="Year", showgrid=False)
    fig.update_yaxes(title="Visits", showgrid=True, gridcolor="rgba(255,255,255,.08)")
    return fig

def shorten_park_label(name: str) -> str:
    if not isinstance(name, str):
        return str(name)
    repl = {
        "National Historical Park": "NHP",
        "National Historic Site": "NHS",
        "National Historic": "NH",
        "National Recreation Area": "NRA",
        "National Recreation": "NR",
        "National Seashore": "NSH",
        "National Monument": "NM",
        "National Park": "NP",
        "Memorial": "MEM",
        "Parkway": "PKWY",
    }
    s = name
    for k, v in repl.items():
        s = s.replace(k, v)
    s = s.strip()
    if len(s) > 26:
        s = s[:23] + "..."
    return s

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
        agg["short"] = agg["State"]  # show only state code on axis
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
        hoverlabel=dict(bgcolor="rgba(10,20,25,.9)", font_color="#ffffff"),
    )
    return fig

# =========================
#  KPI HELPERS
# =========================
def compute_kpis(month_val, year_val, region_val, dest_val, park_type_val):
    month_int = int(month_val)
    year_int  = int(year_val)

    df_month = filter_parks(month_int, year_int, region_val, dest_val, park_type_val)

    if df_month.empty:
        top_park_month = "—"
        total_month = 0.0
        active = 0
        avg = 0.0
    else:
        g = (
            df_month.groupby("Park")["Recreation Visits"]
                    .sum()
                    .sort_values(ascending=False)
        )
        top_park_month = g.index[0]
        total_month = float(g.sum())
        active = g.size
        avg = total_month / max(active, 1)

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
    else:
        g_year = (
            df_year.groupby("Park")["Recreation Visits"]
                   .sum()
                   .sort_values(ascending=False)
        )
        top_park_year = g_year.index[0]

    return {
        "top_park_month": top_park_month,
        "avg_per_park": avg,
        "total_month": total_month,
        "peak_year": peak_year,
        "yoy_pct": yoy_pct,
        "yoy_positive": yoy_pct >= 0,
        "top_park_year": top_park_year,
        "active_parks": active,
    }

# =========================
#  INITIAL FIGURES
# =========================
DEFAULT_MONTH = 7
DEFAULT_YEAR = LATEST_YEAR

df_map_init  = build_base_map_df(DEFAULT_MONTH, DEFAULT_YEAR, "All", "State", "All")
init_map     = build_map(df_map_init)
init_heat    = build_heatmap_real("All", "State", DEFAULT_YEAR, "All")
init_trend   = build_trend_real(DEFAULT_YEAR, "All", "State", "All")
init_bubble  = build_top_park_per_year_bubble("All", "State", "All")
init_top5    = build_top5_parks(DEFAULT_YEAR, "All", "State", "All")

kpi0 = compute_kpis(DEFAULT_MONTH, DEFAULT_YEAR, "All", "State", "All")

# =========================
#  COMPONENTS
# =========================
sidebar_filters = dbc.Card(
    [
        html.Div("Filters", className="kpi-title mb-2"),
        html.Div("Month", className="kpi-title"),
        dcc.Dropdown(
            id="f-month",
            className="dash-dropdown",
            options=[{"label": m, "value": i + 1}
                     for i, m in enumerate(
                        ["January","February","March","April","May","June","July",
                         "August","September","October","November","December"]
                     )],
            value=DEFAULT_MONTH,
            clearable=False,
        ),
        html.Div("Year", className="kpi-title mt-2"),
        dcc.Dropdown(
            id="f-year",
            className="dash-dropdown",
            options=[{"label": str(y), "value": int(y)} for y in YEARS],
            value=DEFAULT_YEAR,
            clearable=False,
        ),
        html.Div("Region", className="kpi-title mt-2"),
        dcc.Dropdown(
            id="f-region",
            className="dash-dropdown",
            options=[{"label": r, "value": r}
                     for r in ["All","East Coast","West","South","Mountain"]],
            value="All",
        ),
        html.Div("Destination Type", className="kpi-title mt-2"),
        dcc.Dropdown(
            id="f-dest",
            className="dash-dropdown",
            options=[{"label": x, "value": x}
                     for x in ["State","City","National Park"]],
            value="State",
        ),
        html.Div("Park Type", className="kpi-title mt-2"),
        dcc.Dropdown(
            id="f-park-type",
            className="dash-dropdown",
            options=(
                [{"label": "All", "value": "All"}] +
                [{"label": t, "value": t}
                 for t in sorted(parks_df["Park Type"].dropna().unique())]
            ),
            value="All",
            clearable=False,
            maxHeight=200,
        ),
    ],
    className="soft-card tight",
    style={"height": MAP_H, "paddingBottom": "18px"},
)

def kpi_card(title, idv):
    return html.Div(
        dbc.Card(
            [
                html.Div(title, className="kpi-title"),
                html.P(id=idv, children="—", className="kpi-value"),
            ],
            className="soft-card tight h-100",
        ),
        className="kpi-col",
    )

kpi_row = html.Div(
    [
        kpi_card("Top Park (Month)", "kpi-top-park-month"),
        kpi_card("Avg Visits / Park", "kpi-avg-park"),
        kpi_card("Total Visitors (Month)", "kpi-total-month"),
        kpi_card("Peak Year", "kpi-peak-year"),
        kpi_card("YoY Growth vs Prev Year", "kpi-yoy"),
        kpi_card("Top Park (Year)", "kpi-top-park-year"),
        kpi_card("Active Parks (Month)", "kpi-active-parks"),
    ],
    className="kpi-row",
    style={"height": KPI_H},
)

map_card = dbc.Card(
    dcc.Graph(
        id="us-map",
        figure=init_map,
        style={"height": "100%", "backgroundColor": "transparent"},
        config={"displayModeBar": False},
    ),
    className="soft-card tight map-card",
    style={"height": MAP_H},
)

heat_card = dbc.Card(
    [
        html.Div("Seasonality Heatmap (Region × Season)", className="kpi-title mb-1"),
        dcc.Graph(
            id="heatmap",
            figure=init_heat,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card tight",
)

trend_card = dbc.Card(
    [
        html.Div("Drilldown — Tourist Inflows (Year)", className="kpi-title mb-1"),
        dcc.Graph(
            id="trend",
            figure=init_trend,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card tight",
)

bubble_card = dbc.Card(
    [
        html.Div("Top Park per Year (Area)", className="kpi-title mb-1"),
        dcc.Graph(
            id="top-park-year-chart",
            figure=init_bubble,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card tight",
)

top5_parks_card = dbc.Card(
    [
        html.Div("Top 5 Parks by Annual Visitors", className="kpi-title mb-1"),
        dcc.Graph(
            id="top5-parks",
            figure=init_top5,
            style={"height": CHART_H},
            config={"displayModeBar": False},
        ),
    ],
    className="soft-card tight",
)

# =========================
#  LAYOUT
# =========================
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Tourist Flow & Seasonality Analyzer",
                             className="section-title"),
                    width=12,
                )
            ],
            className="g-0",
            style={"height": "6vh", "marginTop": TITLE_TOP},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [sidebar_filters],
                    width=4,
                    style={"display": "flex",
                           "flexDirection": "column",
                           "height": COLUMN_H},
                ),
                dbc.Col(
                    [map_card],
                    width=8,
                    style={"display": "flex",
                           "flexDirection": "column",
                           "height": COLUMN_H},
                ),
            ],
            className="gx-3 gy-0",
            # reduced gap between map row and mini-cards row
            style={"marginBottom": "4px"},
        ),
        dbc.Row(
            [dbc.Col(kpi_row, width=12)],
            className="gx-3 gy-0",
            # same gap between mini-cards row and charts row
            style={"marginBottom": "11px"},
        ),
        dbc.Row(
            [
                dbc.Col(heat_card, width=3),
                dbc.Col(trend_card, width=3),
                dbc.Col(bubble_card, width=3),
                dbc.Col(top5_parks_card, width=3),
            ],
            className="gx-3 gy-0",
        ),
    ],
    fluid=True,
    className="dbc-container pb-2",
    style={"height": "100vh", "overflow": "hidden"},
)

# =========================
#  CALLBACKS — FIGURES
# =========================
@app.callback(
    [
        Output("us-map", "figure"),
        Output("heatmap", "figure"),
        Output("trend", "figure"),
        Output("top-park-year-chart", "figure"),
        Output("top5-parks", "figure"),
    ],
    [
        Input("f-month", "value"),
        Input("f-year", "value"),
        Input("f-region", "value"),
        Input("f-dest", "value"),
        Input("f-park-type", "value"),
    ],
)
def update_all(month_val, year_val, region_val, dest_val, park_type_val):
    dfm = build_base_map_df(month_val, year_val, region_val, dest_val, park_type_val)
    map_out   = build_map(dfm)
    heat_out  = build_heatmap_real(region_val, dest_val, year_val, park_type_val)
    trend_out = build_trend_real(year_val, region_val, dest_val, park_type_val)
    bubble_out = build_top_park_per_year_bubble(region_val, dest_val, park_type_val)
    top5_out  = build_top5_parks(year_val, region_val, dest_val, park_type_val)
    return map_out, heat_out, trend_out, bubble_out, top5_out

# =========================
#  CALLBACKS — KPIs
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
        Output("kpi-active-parks", "children"),
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
        f"{k['total_month']:,.0f}",
        str(k["peak_year"]),
        yoy_text,
        yoy_style,
        k["top_park_year"],
        str(k["active_parks"]),
    )

# =========================
#  RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)