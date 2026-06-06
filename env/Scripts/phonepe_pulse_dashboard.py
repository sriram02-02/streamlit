import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PhonePe Pulse Analytics",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS  – PhonePe dark-purple brand feel
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;900&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1a0533 0%, #2d1458 100%);
    border-right: 1px solid #5a2d9a33;
}
[data-testid="stSidebar"] * { color: #e8d5ff !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #c9a8ff !important; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; }

/* Main background */
.stApp { background: #0d0120; color: #f0e6ff; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1e0540 0%, #2d1458 100%);
    border: 1px solid #6b35c855;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 24px #7c3aed22;
}
.metric-card h3 { color: #c084fc; font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; margin: 0 0 0.3rem; font-family: 'Space Mono', monospace; }
.metric-card p  { color: #f0e6ff; font-size: 1.9rem; font-weight: 900; margin: 0; }
.metric-card span { color: #a78bfa; font-size: 0.82rem; }

/* Section headers */
.section-title {
    font-size: 1.5rem; font-weight: 900;
    background: linear-gradient(90deg, #c084fc, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 1.5rem 0 0.3rem;
}
.section-sub { color: #9d7ec7; font-size: 0.9rem; margin-bottom: 1.2rem; }

/* Case header pill */
.case-pill {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #4f46e5);
    color: white !important;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    padding: 0.25rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 0.6rem;
    letter-spacing: 0.08em;
}

/* Plotly chart bg override */
.js-plotly-plot .plotly { border-radius: 12px; }

/* Tabs */
[data-testid="stTabs"] button {
    color: #a78bfa !important;
    font-weight: 700;
    font-size: 0.85rem;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #f0e6ff !important;
    border-bottom-color: #c084fc !important;
}

/* Divider */
hr { border-color: #5a2d9a33; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1a0533; }
::-webkit-scrollbar-thumb { background: #6b35c8; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,1,32,0.6)",
    font_color="#e8d5ff",
    colorway=["#a855f7", "#818cf8", "#34d399", "#f472b6", "#fbbf24", "#60a5fa"],
)

def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(color=CHART_THEME["font_color"], family="Nunito"),
        xaxis=dict(gridcolor="#2d1458", linecolor="#5a2d9a"),
        yaxis=dict(gridcolor="#2d1458", linecolor="#5a2d9a"),
    )
    return fig

# ─────────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────────
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "NewStrongPassword123"   # ← your MySQL password
DB_NAME     = "phonepe"
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )

@st.cache_data(ttl=300)
def run_query(sql):
    conn = get_connection()
    return pd.read_sql(sql, conn)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💜 PhonePe Pulse")
    st.markdown("---")
    case = st.selectbox(
    "SELECT BUSINESS CASE",
    [
        "🔄 Transaction Dynamics",
        "📱 Device & User Engagement",
        "🛡️ Insurance Penetration",
        "🗺️ Market Expansion",
        "👥 User Growth Strategy",
    ],
)
    st.markdown("---")
    st.markdown("<span style='font-size:0.72rem;color:#6b35c8;font-family:Space Mono'>FILTERS</span>", unsafe_allow_html=True)

    years = run_query("SELECT DISTINCT year FROM agg_transaction ORDER BY year")["year"].tolist()
    sel_year = st.selectbox("Year", ["All"] + years)

    quarters = [1, 2, 3, 4]
    sel_quarter = st.selectbox("Quarter", ["All"] + quarters)

    st.markdown("---")
    st.markdown("<div style='font-size:0.7rem;color:#6b35c8;text-align:center'>Data via PhonePe Pulse · MySQL</div>", unsafe_allow_html=True)

def year_filter(col="year"):
    return f"AND {col} = '{sel_year}'" if sel_year != "All" else ""

def quarter_filter(col="quarter"):
    return f"AND {col} = {sel_quarter}" if sel_quarter != "All" else ""

def fmt_cr(val):
    """Format large numbers as Cr / L / K"""
    if val >= 1e7:   return f"₹{val/1e7:.1f} Cr"
    if val >= 1e5:   return f"₹{val/1e5:.1f} L"
    return f"₹{val:,.0f}"

def fmt_num(val):
    if val >= 1e9:  return f"{val/1e9:.2f}B"
    if val >= 1e6:  return f"{val/1e6:.2f}M"
    if val >= 1e3:  return f"{val/1e3:.1f}K"
    return str(int(val))

# ═══════════════════════════════════════════════════════════════════
# CASE 1 – TRANSACTION DYNAMICS
# ═══════════════════════════════════════════════════════════════════
if case == "🔄 Transaction Dynamics":
    st.markdown('<div class="case-pill">BUSINESS CASE 01</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Decoding Transaction Dynamics on PhonePe</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Analysing transaction behaviour across states, quarters, and payment categories</div>', unsafe_allow_html=True)

    yf, qf = year_filter(), quarter_filter()

    # KPIs
    kpi = run_query(f"""
        SELECT SUM(transaction_count) total_txn,
               SUM(transaction_amount) total_amt,
               COUNT(DISTINCT state) states,
               COUNT(DISTINCT transaction_type) types
        FROM agg_transaction WHERE 1=1 {yf} {qf}
    """).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Total Transactions",  fmt_num(kpi["total_txn"]),  "across all states"),
        (c2, "Total Amount",        fmt_cr(kpi["total_amt"]),   "transacted"),
        (c3, "States Covered",      int(kpi["states"]),         "active states"),
        (c4, "Payment Categories",  int(kpi["types"]),          "transaction types"),
    ]:
        col.markdown(f"""<div class="metric-card"><h3>{label}</h3><p>{val}</p><span>{sub}</span></div>""", unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📊 Category Breakdown", "📈 Quarterly Trends", "🗺️ State Heatmap"])

    with tab1:
        df = run_query(f"""
            SELECT transaction_type,
                   SUM(transaction_count) txn_count,
                   SUM(transaction_amount) txn_amount
            FROM agg_transaction WHERE 1=1 {yf} {qf}
            GROUP BY transaction_type ORDER BY txn_amount DESC
        """)
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df, x="transaction_type", y="txn_count",
                         color="transaction_type", title="Transaction Count by Category",
                         labels={"txn_count": "Count", "transaction_type": "Type"},
                         color_discrete_sequence=CHART_THEME["colorway"])
            apply_theme(fig); fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df, names="transaction_type", values="txn_amount",
                         title="Transaction Amount Share",
                         color_discrete_sequence=CHART_THEME["colorway"], hole=0.45)
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = run_query(f"""
            SELECT year, quarter,
                   SUM(transaction_count) txn_count,
                   SUM(transaction_amount) txn_amount
            FROM agg_transaction WHERE 1=1 {yf} {qf}
            GROUP BY year, quarter ORDER BY year, quarter
        """)
        df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=df["period"], y=df["txn_count"], name="Txn Count", marker_color="#a855f7"), secondary_y=False)
        fig.add_trace(go.Scatter(x=df["period"], y=df["txn_amount"], name="Txn Amount (₹)", mode="lines+markers", line=dict(color="#34d399", width=2)), secondary_y=True)
        fig.update_layout(title="Quarterly Transaction Trends", **{k: v for k, v in CHART_THEME.items() if k != "colorway"}, font=dict(color="#e8d5ff"))
        apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df = run_query(f"""
            SELECT state,
                   SUM(transaction_count) txn_count,
                   SUM(transaction_amount) txn_amount,
                   AVG(transaction_amount/NULLIF(transaction_count,0)) avg_txn
            FROM agg_transaction WHERE 1=1 {yf} {qf}
            GROUP BY state ORDER BY txn_amount DESC LIMIT 20
        """)
        fig = px.bar(df, x="txn_amount", y="state", orientation="h",
                     color="avg_txn", color_continuous_scale="Purples",
                     title="Top 20 States – Transaction Amount & Avg Ticket Size",
                     labels={"txn_amount": "Total Amount (₹)", "state": "State", "avg_txn": "Avg Ticket (₹)"})
        apply_theme(fig)
        fig.update_layout(height=560)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CASE 2 – DEVICE & USER ENGAGEMENT
# ═══════════════════════════════════════════════════════════════════
elif case == "📱 Device & User Engagement":
    st.markdown('<div class="case-pill">BUSINESS CASE 02</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Device Dominance & User Engagement Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Understanding user preferences across device brands, regions, and time periods</div>', unsafe_allow_html=True)

    yf, qf = year_filter(), quarter_filter()

    kpi = run_query(f"""
        SELECT SUM(Registered_users) total_users,
               SUM(app_opens) total_opens,
               COUNT(DISTINCT brand) brands,
               COUNT(DISTINCT state) states
        FROM agg_user WHERE 1=1 {yf} {qf}
    """).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Registered Users",  fmt_num(kpi["total_users"]), "total users"),
        (c2, "App Opens",         fmt_num(kpi["total_opens"]), "total opens"),
        (c3, "Device Brands",     int(kpi["brands"]),          "tracked brands"),
        (c4, "States",            int(kpi["states"]),          "covered"),
    ]:
        col.markdown(f"""<div class="metric-card"><h3>{label}</h3><p>{val}</p><span>{sub}</span></div>""", unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📱 Brand Analysis", "📊 Engagement Ratio", "🌍 State-wise Users"])

    with tab1:
        df = run_query(f"""
            SELECT brand,
                   SUM(Registered_users) reg_users,
                   SUM(app_opens) opens,
                   AVG(percentage) avg_pct
            FROM agg_user WHERE brand IS NOT NULL {yf} {qf}
            GROUP BY brand ORDER BY reg_users DESC LIMIT 15
        """)
        fig = px.bar(df, x="brand", y="reg_users",
                     color="avg_pct", color_continuous_scale="Purples",
                     title="Registered Users by Device Brand",
                     labels={"reg_users": "Registered Users", "brand": "Brand", "avg_pct": "Market %"})
        apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        # Opens vs Users scatter
        fig2 = px.scatter(df, x="reg_users", y="opens", size="avg_pct",
                          text="brand", title="App Opens vs Registered Users by Brand",
                          color="avg_pct", color_continuous_scale="Purpor",
                          labels={"reg_users": "Registered Users", "opens": "App Opens"})
        apply_theme(fig2)
        fig2.update_traces(textposition="top center")
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        df = run_query(f"""
            SELECT brand,
                   SUM(app_opens) opens,
                   SUM(Registered_users) reg_users,
                   ROUND(SUM(app_opens)/NULLIF(SUM(Registered_users),0),2) engagement_ratio
            FROM agg_user WHERE brand IS NOT NULL {yf} {qf}
            GROUP BY brand HAVING reg_users > 0 ORDER BY engagement_ratio DESC LIMIT 15
        """)
        fig = px.bar(df, x="engagement_ratio", y="brand", orientation="h",
                     color="engagement_ratio", color_continuous_scale=["#2d1458","#a855f7","#f0e6ff"],
                     title="App Opens per Registered User (Engagement Ratio)",
                     labels={"engagement_ratio": "Opens / User", "brand": "Brand"})
        apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 A high ratio means existing users open the app frequently. Low ratio + high registration = underutilised potential.")

    with tab3:
        df = run_query(f"""
            SELECT state,
                   SUM(Registered_users) reg_users,
                   SUM(app_opens) opens
            FROM map_user WHERE 1=1 {yf} {qf}
            GROUP BY state ORDER BY reg_users DESC LIMIT 20
        """)
        fig = px.bar(df, x="state", y=["reg_users", "opens"],
                     barmode="group", title="Top 20 States – Users vs App Opens",
                     color_discrete_sequence=["#a855f7", "#34d399"],
                     labels={"value": "Count", "state": "State", "variable": "Metric"})
        apply_theme(fig)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CASE 3 – INSURANCE PENETRATION
# ═══════════════════════════════════════════════════════════════════
elif case == "🛡️ Insurance Penetration":
    st.markdown('<div class="case-pill">BUSINESS CASE 03</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Insurance Penetration & Growth Potential</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Identifying untapped insurance opportunities and high-priority states for marketing</div>', unsafe_allow_html=True)

    yf, qf = year_filter(), quarter_filter()

    kpi = run_query(f"""
        SELECT SUM(insured_count) total_insured,
               SUM(insured_amount) total_amount,
               COUNT(DISTINCT state) states,
               COUNT(DISTINCT insurance_type) types
        FROM agg_insurance WHERE 1=1 {yf} {qf}
    """).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Total Policies",    fmt_num(kpi["total_insured"]), "insured count"),
        (c2, "Total Premium",     fmt_cr(kpi["total_amount"]),  "insured amount"),
        (c3, "States Active",     int(kpi["states"]),           "states"),
        (c4, "Insurance Types",   int(kpi["types"]),            "product types"),
    ]:
        col.markdown(f"""<div class="metric-card"><h3>{label}</h3><p>{val}</p><span>{sub}</span></div>""", unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📈 Growth Trajectory", "🏆 Top States", "📍 District Leaders"])

    with tab1:
        df = run_query(f"""
            SELECT year, quarter,
                   SUM(insured_count) policies,
                   SUM(insured_amount) amount
            FROM agg_insurance WHERE 1=1 {yf} {qf}
            GROUP BY year, quarter ORDER BY year, quarter
        """)
        df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
        df["q_growth"] = df["policies"].pct_change() * 100

        fig = make_subplots(rows=2, cols=1, subplot_titles=("Policies Over Time", "Quarter-on-Quarter Growth (%)"))
        fig.add_trace(go.Scatter(x=df["period"], y=df["policies"], fill="tozeroy",
                                  line=dict(color="#a855f7"), fillcolor="rgba(168,85,247,0.15)", name="Policies"), row=1, col=1)
        fig.add_trace(go.Bar(x=df["period"], y=df["q_growth"],
                              marker_color=["#34d399" if v >= 0 else "#f472b6" for v in df["q_growth"].fillna(0)],
                              name="QoQ Growth %"), row=2, col=1)
        apply_theme(fig); fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = run_query(f"""
            SELECT state,
                   SUM(insured_count) policies,
                   SUM(insured_amount) amount,
                   AVG(insured_amount/NULLIF(insured_count,0)) avg_premium
            FROM agg_insurance WHERE 1=1 {yf} {qf}
            GROUP BY state ORDER BY policies DESC LIMIT 20
        """)
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.bar(df.head(10), x="policies", y="state", orientation="h",
                         color="policies", color_continuous_scale="Purples",
                         title="Top 10 States by Policy Count",
                         labels={"policies": "Policies", "state": "State"})
            apply_theme(fig); st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.scatter(df, x="policies", y="avg_premium", size="amount",
                             color="state", title="Policy Volume vs Avg Premium",
                             labels={"policies": "Policy Count", "avg_premium": "Avg Premium (₹)"},
                             color_discrete_sequence=CHART_THEME["colorway"])
            apply_theme(fig); st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df = run_query(f"""
            SELECT state, district,
                   SUM(insured_count) policies,
                   SUM(insured_amount) amount
            FROM top_insurance WHERE 1=1 {yf} {qf}
            GROUP BY state, district ORDER BY policies DESC LIMIT 20
        """)
        fig = px.treemap(df, path=["state", "district"], values="policies",
                         color="amount", color_continuous_scale="Purpor",
                         title="Top Districts by Insurance Policies (Treemap)")
        apply_theme(fig); fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CASE 4 – MARKET EXPANSION
# ═══════════════════════════════════════════════════════════════════
elif case == "🗺️ Market Expansion":
    st.markdown('<div class="case-pill">BUSINESS CASE 04</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Transaction Analysis for Market Expansion</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Identifying high-growth states, saturated markets, and untapped expansion zones</div>', unsafe_allow_html=True)

    yf, qf = year_filter(), quarter_filter()

    tab1, tab2, tab3 = st.tabs(["🏅 State Rankings", "🔍 District Deep-Dive", "📊 Growth Opportunities"])

    with tab1:
        df = run_query(f"""
            SELECT state,
                   SUM(transaction_count) txn_count,
                   SUM(transaction_amount) txn_amount,
                   AVG(transaction_amount/NULLIF(transaction_count,0)) avg_ticket
            FROM agg_transaction WHERE 1=1 {yf} {qf}
            GROUP BY state ORDER BY txn_amount DESC
        """)
        st.markdown("#### State Transaction Leaderboard")
        # Color-coded dataframe
        df_disp = df.copy()
        df_disp["txn_amount"] = df_disp["txn_amount"].apply(lambda x: fmt_cr(x))
        df_disp["txn_count"]  = df_disp["txn_count"].apply(lambda x: fmt_num(x))
        df_disp["avg_ticket"] = df_disp["avg_ticket"].apply(lambda x: f"₹{x:,.0f}")
        df_disp.columns = ["State", "Txn Count", "Txn Amount", "Avg Ticket Size"]
        st.dataframe(df_disp, use_container_width=True, height=400)

        # Bubble chart
        df2 = run_query(f"""
            SELECT state,
                   SUM(transaction_count) txn_count,
                   SUM(transaction_amount) txn_amount,
                   AVG(transaction_amount/NULLIF(transaction_count,0)) avg_ticket
            FROM agg_transaction WHERE 1=1 {yf} {qf}
            GROUP BY state
        """)
        fig = px.scatter(df2, x="txn_count", y="avg_ticket", size="txn_amount",
                         color="state", title="State Segmentation: Volume vs Avg Ticket",
                         labels={"txn_count": "Transaction Count", "avg_ticket": "Avg Ticket Size (₹)"},
                         color_discrete_sequence=CHART_THEME["colorway"])
        apply_theme(fig); fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        states = run_query("SELECT DISTINCT state FROM map_transaction ORDER BY state")["state"].tolist()
        sel_state = st.selectbox("Select State", states)
        df = run_query(f"""
            SELECT district,
                   SUM(transaction_count) txn_count,
                   SUM(transaction_amount) txn_amount
            FROM map_transaction
            WHERE state = '{sel_state}' {yf} {qf}
            GROUP BY district ORDER BY txn_amount DESC LIMIT 15
        """)
        fig = px.bar(df, x="district", y="txn_amount",
                     color="txn_count", color_continuous_scale="Purples",
                     title=f"Top Districts in {sel_state}",
                     labels={"txn_amount": "Txn Amount (₹)", "district": "District", "txn_count": "Txn Count"})
        apply_theme(fig); fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df = run_query(f"""
            SELECT a.state,
                   SUM(a.transaction_count) agg_count,
                   SUM(m.transaction_count) map_count,
                   SUM(a.transaction_amount) agg_amt,
                   SUM(m.transaction_amount) map_amt
            FROM agg_transaction a
            LEFT JOIN map_transaction m ON a.state = m.state
              AND a.year = m.year AND a.quarter = m.quarter
            WHERE 1=1 {yf} {qf}
            GROUP BY a.state ORDER BY agg_amt DESC LIMIT 20
        """)
        df["district_opportunity"] = df["map_count"] / df["agg_count"].replace(0, 1)
        fig = px.bar(df, x="state", y="district_opportunity",
                     color="district_opportunity",
                     color_continuous_scale=["#2d1458", "#a855f7", "#34d399"],
                     title="District Transaction Concentration Ratio (higher = more distributed)",
                     labels={"district_opportunity": "District/State Ratio", "state": "State"})
        apply_theme(fig); fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 States with low ratio concentrate transactions in few districts — high expansion potential in underserved areas.")

# ═══════════════════════════════════════════════════════════════════
# CASE 5 – USER GROWTH STRATEGY
# ═══════════════════════════════════════════════════════════════════
elif case == "👥 User Growth Strategy":
    st.markdown('<div class="case-pill">BUSINESS CASE 05</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">User Engagement & Growth Strategy</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Analysing registered users and app opens across states and districts for strategic growth</div>', unsafe_allow_html=True)

    yf, qf = year_filter(), quarter_filter()

    kpi = run_query(f"""
        SELECT SUM(Registered_users) total_users,
               SUM(app_opens) total_opens,
               COUNT(DISTINCT state) states
        FROM map_user WHERE 1=1 {yf} {qf}
    """).iloc[0]

    c1, c2, c3 = st.columns(3)
    for col, label, val, sub in [
        (c1, "Total Registered Users", fmt_num(kpi["total_users"]), "registered"),
        (c2, "Total App Opens",        fmt_num(kpi["total_opens"]), "opens"),
        (c3, "States Active",          int(kpi["states"]),          "states"),
    ]:
        col.markdown(f"""<div class="metric-card"><h3>{label}</h3><p>{val}</p><span>{sub}</span></div>""", unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📈 Growth Over Time", "🏙️ District Opportunities", "🎯 Engagement Matrix"])

    with tab1:
        df = run_query(f"""
            SELECT year, quarter,
                   SUM(Registered_users) users,
                   SUM(app_opens) opens
            FROM map_user WHERE 1=1 {yf} {qf}
            GROUP BY year, quarter ORDER BY year, quarter
        """)
        df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
        df["user_growth"] = df["users"].pct_change() * 100

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Users & Opens Over Time", "Quarter-on-Quarter User Growth %"))
        fig.add_trace(go.Scatter(x=df["period"], y=df["users"], name="Registered Users",
                                  line=dict(color="#a855f7", width=2.5), fill="tozeroy",
                                  fillcolor="rgba(168,85,247,0.1)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["period"], y=df["opens"], name="App Opens",
                                  line=dict(color="#34d399", width=2, dash="dot")), row=1, col=1)
        fig.add_trace(go.Bar(x=df["period"], y=df["user_growth"],
                              marker_color=["#34d399" if v >= 0 else "#f472b6" for v in df["user_growth"].fillna(0)],
                              name="Growth %"), row=1, col=2)
        apply_theme(fig); fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        states = run_query("SELECT DISTINCT state FROM top_user ORDER BY state")["state"].tolist()
        sel_state = st.selectbox("Pick a State", states)
        df = run_query(f"""
            SELECT district, SUM(Registered_users) users
            FROM top_user
            WHERE state = '{sel_state}' {yf} {qf}
            GROUP BY district ORDER BY users DESC LIMIT 15
        """)
        fig = px.bar(df, x="users", y="district", orientation="h",
                     color="users", color_continuous_scale="Purples",
                     title=f"Top Districts by Registered Users – {sel_state}",
                     labels={"users": "Registered Users", "district": "District"})
        apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df = run_query(f"""
            SELECT state,
                   SUM(Registered_users) users,
                   SUM(app_opens) opens,
                   ROUND(SUM(app_opens)/NULLIF(SUM(Registered_users),0),2) eng_ratio
            FROM map_user WHERE 1=1 {yf} {qf}
            GROUP BY state
        """)
        # Quadrant segmentation
        med_users = df["users"].median()
        med_eng   = df["eng_ratio"].median()

        def segment(row):
            if row["users"] >= med_users and row["eng_ratio"] >= med_eng: return "⭐ Champions"
            if row["users"] >= med_users and row["eng_ratio"] <  med_eng: return "😴 Dormant Giants"
            if row["users"] <  med_users and row["eng_ratio"] >= med_eng: return "🚀 Rising Stars"
            return "⚡ Untapped"

        df["segment"] = df.apply(segment, axis=1)
        fig = px.scatter(df, x="users", y="eng_ratio", color="segment", text="state",
                         title="User Engagement Matrix — State Segmentation",
                         labels={"users": "Registered Users", "eng_ratio": "Engagement Ratio (Opens/User)"},
                         color_discrete_map={
                             "⭐ Champions":    "#a855f7",
                             "😴 Dormant Giants": "#f472b6",
                             "🚀 Rising Stars":  "#34d399",
                             "⚡ Untapped":      "#fbbf24",
                         })
        apply_theme(fig)
        fig.update_traces(textposition="top center", textfont_size=9)
        fig.add_hline(y=med_eng,   line_dash="dot", line_color="#5a2d9a99")
        fig.add_vline(x=med_users, line_dash="dot", line_color="#5a2d9a99")
        fig.update_layout(height=560)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Segment Guide**")
        st.markdown("""
        - ⭐ **Champions** — High users + High engagement: Leverage for referrals & premium features  
        - 😴 **Dormant Giants** — High users + Low engagement: Re-engagement campaigns needed  
        - 🚀 **Rising Stars** — Low users + High engagement: Ripe for user acquisition investment  
        - ⚡ **Untapped** — Low users + Low engagement: Ground-level awareness & adoption drives  
        """)
