import json
import math
import os
from datetime import datetime
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pe_core import (
    FIRM_CONFIGS,
    ai_signal_count,
    build_ai_context,
    build_why_now,
    classify_news_signal,
    compute_data_confidence,
    compute_opportunity_score,
    detect_technology_signals,
    enrich_job_description,
    extract_skills,
    get_google_news,
    get_official_description,
    get_official_news_cards,
    get_profile_bio,
    get_public_jobs,
    get_public_leadership,
    get_public_portfolio,
    get_wikipedia_summary,
    job_relevance,
    leader_reason,
    load_capabilities,
    load_local_insights,
    load_local_jobs,
    load_local_leadership,
    load_local_portfolio,
    make_account_brief_markdown,
    map_ai_opportunities,
    merge_insights,
    normalize_insights,
    normalize_jobs,
    normalize_leadership,
    normalize_portfolio,
    opportunity_score_breakdown,
    parse_uploaded_file,
    run_ai_analysis,
    score_band,
    skills_relevant_to_coforge,
    source_coverage,
    tech_evidence,
)


# =============================================================================
# PAGE CONFIG + DESIGN SYSTEM
# =============================================================================
st.set_page_config(
    page_title="Coforge PE Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f5f7fb;
        --panel: rgba(255,255,255,.96);
        --panel-2: #fbfcff;
        --ink: #0f172a;
        --muted: #64748b;
        --line: #e6eaf2;
        --brand: #635bff;
        --brand-deep: #3427b6;
        --cyan: #0ea5e9;
        --green: #16a34a;
        --amber: #d97706;
        --red: #dc2626;
        --nav: #101423;
        --nav2: #171c30;
    }

    html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .stApp {
        background:
          radial-gradient(circle at 85% 2%, rgba(99,91,255,.09), transparent 25rem),
          radial-gradient(circle at 22% 20%, rgba(14,165,233,.045), transparent 23rem),
          var(--bg);
        color: var(--ink);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--nav) 0%, var(--nav2) 100%);
        border-right: 1px solid rgba(255,255,255,.06);
    }
    [data-testid="stSidebar"] * { color: #eef2ff; }
    [data-testid="stSidebar"] label { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] input {
        background-color: rgba(255,255,255,.08) !important;
        border-color: rgba(255,255,255,.12) !important;
        color: white !important;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.08); }

    .block-container {
        max-width: 1540px;
        padding-top: 1.1rem;
        padding-bottom: 3.5rem;
    }

    .brand-lockup { margin-bottom: .35rem; }
    .brand-mark {
        width: 30px; height: 30px; border-radius: 9px;
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #8b5cf6, #4f46e5);
        color: white; font-weight: 900; margin-right: 8px;
        box-shadow: 0 8px 20px rgba(99,91,255,.35);
    }
    .brand-title { font-weight: 780; font-size: 1.05rem; vertical-align: middle; }
    .brand-sub { color:#94a3b8; font-size:.74rem; margin-top:.25rem; }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 1.5rem 1.65rem 1.35rem;
        border-radius: 22px;
        background:
          radial-gradient(circle at 90% 30%, rgba(118,97,255,.48), transparent 23rem),
          linear-gradient(120deg, #0c1324 0%, #1b1d42 55%, #322585 100%);
        box-shadow: 0 20px 52px rgba(21,25,54,.16);
        color:white;
        margin-bottom: 1rem;
    }
    .hero:after {
        content:""; position:absolute; width:340px; height:340px; border-radius:50%;
        border:1px solid rgba(255,255,255,.07); right:-110px; top:-155px;
    }
    .hero-kicker { color:#c4b5fd; font-size:.72rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
    .hero-title { font-size:2.05rem; line-height:1.08; font-weight:800; margin:.35rem 0 .35rem; letter-spacing:-.03em; }
    .hero-sub { color:#dbeafe; font-size:.93rem; max-width:930px; }
    .hero-meta { color:#a5b4fc; font-size:.78rem; margin-top:.65rem; }

    .kpi-card, .glass-card, .signal-card, .leader-card, .news-card, .op-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 16px;
        box-shadow: 0 9px 26px rgba(15,23,42,.045);
    }
    .kpi-card { padding: .95rem 1rem; min-height:108px; }
    .kpi-label { color:var(--muted); font-size:.69rem; font-weight:800; letter-spacing:.075em; text-transform:uppercase; }
    .kpi-value { color:var(--ink); font-size:1.65rem; font-weight:800; letter-spacing:-.03em; margin:.25rem 0 .08rem; }
    .kpi-note { color:#7c879a; font-size:.73rem; line-height:1.3; }
    .glass-card { padding:1rem 1.05rem; }
    .card-title { font-size:.95rem; font-weight:760; color:#172033; margin-bottom:.3rem; }
    .card-copy { font-size:.86rem; color:#64748b; line-height:1.52; }

    .section-kicker { color:#6366f1; font-size:.69rem; font-weight:800; letter-spacing:.09em; text-transform:uppercase; margin-bottom:.1rem; }
    .section-title { color:#111827; font-size:1.12rem; font-weight:800; letter-spacing:-.01em; margin:.05rem 0 .45rem; }
    .section-sub { color:#64748b; font-size:.84rem; margin-bottom:.65rem; }

    .badge {
        display:inline-block; padding:.22rem .5rem; border-radius:999px; font-size:.68rem; font-weight:750;
        margin:0 .15rem .15rem 0; border:1px solid transparent;
    }
    .badge-purple { background:#eef2ff; color:#4f46e5; border-color:#e0e7ff; }
    .badge-green { background:#ecfdf5; color:#15803d; border-color:#d1fae5; }
    .badge-amber { background:#fffbeb; color:#b45309; border-color:#fef3c7; }
    .badge-blue { background:#eff6ff; color:#1d4ed8; border-color:#dbeafe; }
    .badge-gray { background:#f8fafc; color:#64748b; border-color:#e2e8f0; }
    .badge-red { background:#fef2f2; color:#b91c1c; border-color:#fee2e2; }

    .signal-card { padding:.85rem .9rem; margin-bottom:.55rem; }
    .signal-top { display:flex; align-items:center; justify-content:space-between; gap:.75rem; }
    .signal-name { font-weight:760; color:#172033; font-size:.9rem; }
    .signal-copy { color:#64748b; font-size:.78rem; margin-top:.25rem; line-height:1.42; }

    .score-ring-wrap { display:flex; align-items:center; gap:1rem; }
    .score-number { font-size:2.45rem; font-weight:850; letter-spacing:-.06em; color:#111827; }
    .score-label { font-size:.78rem; color:#64748b; }

    .data-row { display:flex; align-items:center; justify-content:space-between; padding:.52rem 0; border-bottom:1px solid #eef2f7; }
    .data-row:last-child { border-bottom:none; }
    .data-label { color:#334155; font-size:.82rem; font-weight:700; }
    .data-meta { color:#64748b; font-size:.75rem; }

    .news-card { padding:.9rem 1rem; margin-bottom:.55rem; }
    .news-title { color:#172033; font-size:.91rem; font-weight:760; line-height:1.35; }
    .news-summary { color:#64748b; font-size:.78rem; line-height:1.48; margin-top:.35rem; }
    .news-meta { color:#94a3b8; font-size:.68rem; margin-top:.38rem; }

    .op-card { padding:1rem; height:100%; }
    .op-head { display:flex; justify-content:space-between; gap:.8rem; align-items:flex-start; }
    .op-name { color:#172033; font-size:.92rem; font-weight:800; }
    .op-copy { color:#64748b; font-size:.79rem; line-height:1.48; margin-top:.4rem; }
    .op-evidence { color:#475569; font-size:.72rem; margin-top:.55rem; padding-top:.5rem; border-top:1px solid #edf0f5; }

    .person-detail {
        background: linear-gradient(135deg, #ffffff, #f8f8ff);
        border:1px solid #e3e6ef; border-radius:17px; padding:1rem 1.05rem; margin-bottom:.75rem;
    }
    .person-name { font-size:1.08rem; font-weight:820; color:#111827; }
    .person-role { font-size:.83rem; color:#4f46e5; font-weight:720; margin:.14rem 0 .4rem; }
    .person-bio { font-size:.82rem; color:#64748b; line-height:1.52; }

    .empty-state { background:#fff; border:1px dashed #cbd5e1; border-radius:16px; padding:1.2rem; color:#64748b; }
    .scope-note { background:#fffaf0; border:1px solid #fde7b3; color:#7c5b16; padding:.72rem .85rem; border-radius:12px; font-size:.77rem; line-height:1.45; }

    div[data-testid="stMetric"] { background:white; border:1px solid var(--line); border-radius:15px; padding:.75rem .9rem; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {
        border-radius:10px !important; font-weight:680 !important; min-height:2.5rem;
    }
    .stTabs [data-baseweb="tab-list"] { gap:.35rem; }
    .stTabs [data-baseweb="tab"] { border-radius:9px; padding:.45rem .75rem; }
    #MainMenu, footer {visibility:hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# UI HELPERS
# =============================================================================
def section_title(title, sub=None, kicker=None):
    if kicker:
        st.markdown(f'<div class="section-kicker">{escape(kicker)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{escape(sub)}</div>', unsafe_allow_html=True)


def kpi_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{escape(str(label))}</div>
            <div class="kpi-value">{escape(str(value))}</div>
            <div class="kpi-note">{escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text, kind="purple"):
    return f'<span class="badge badge-{kind}">{escape(str(text))}</span>'


def strength_badge(score):
    if score >= 5:
        return badge("Very strong", "green")
    if score >= 4:
        return badge("Strong", "green")
    if score >= 3:
        return badge("Medium", "amber")
    return badge("Early", "gray")


def priority_badge(score):
    if score >= 75:
        return badge("High priority", "green")
    if score >= 55:
        return badge("Developing", "blue")
    if score >= 35:
        return badge("Watchlist", "amber")
    return badge("Unqualified", "gray")


def relevance_badge(score):
    if score >= 5:
        return badge("5/5 Coforge fit", "green")
    if score >= 4:
        return badge("4/5 Coforge fit", "blue")
    if score >= 3:
        return badge("3/5 Coforge fit", "amber")
    return badge(f"{score}/5 fit", "gray")


def hero(firm, score, coverage_score, latest_count):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">COFORGE · PRIVATE EQUITY ACCOUNT INTELLIGENCE</div>
            <div class="hero-title">{escape(firm['name'])}</div>
            <div class="hero-sub">{escape(firm['category'])} · Portfolio, people, hiring, technology, news and evidence-based AI opportunity intelligence in one workspace.</div>
            <div class="hero-meta">Priority {score}/100 &nbsp;·&nbsp; Data confidence {coverage_score}% &nbsp;·&nbsp; {latest_count} intelligence items loaded</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_button(label, target, key):
    if st.button(label, key=key, use_container_width=True):
        st.session_state.page = target
        st.rerun()


def display_news_card(article, compact=False):
    title = escape(article.get("title") or "Untitled")
    summary = escape((article.get("summary") or "")[:350 if compact else 650])
    source = escape(article.get("source") or "News")
    published = escape(article.get("published") or "")
    signal = escape(article.get("signal_type") or "Other")
    link = article.get("link") or ""
    html = f"""
    <div class="news-card">
        <div>{badge(signal, 'purple')} {badge(source, 'gray')}</div>
        <div class="news-title">{title}</div>
        {f'<div class="news-summary">{summary}</div>' if summary else ''}
        <div class="news-meta">{published}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    if link:
        st.link_button("Open source ↗", link, use_container_width=compact)


def safe_unique(values):
    return sorted({str(x).strip() for x in values if str(x).strip() and str(x).strip().lower() not in {"nan", "none"}})


def source_mode(session_key, firm_key, local_data, public_data, public_label):
    uploaded = st.session_state[session_key].get(firm_key)
    if uploaded:
        return "Session upload"
    if local_data:
        return "Local data file"
    if public_data:
        return public_label
    return "Not available"


# =============================================================================
# STATE
# =============================================================================
def ensure_state(name, default):
    if name not in st.session_state:
        st.session_state[name] = default


ensure_state("page", "Command Center")
ensure_state("uploaded_portfolio", {})
ensure_state("uploaded_jobs", {})
ensure_state("uploaded_insights", {})
ensure_state("uploaded_leadership", {})
ensure_state("analysis_history", [])
ensure_state("selected_person", {})
ensure_state("selected_portco", {})


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><span class="brand-mark">◆</span><span class="brand-title">PE Intelligence</span><div class="brand-sub">Coforge account intelligence workspace</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    firm_keys = list(FIRM_CONFIGS.keys())
    firm_search = st.text_input(
        "Find a PE firm",
        placeholder="Type KKR, CVC, Pereira, Bridgepoint…",
        help="Searches firm names and aliases. For example, typing 'Pereira' resolves to Permira.",
    )
    if firm_search.strip():
        needle = firm_search.strip().lower()
        matched_firms = [
            key for key in firm_keys
            if needle in FIRM_CONFIGS[key]["name"].lower()
            or any(needle in alias.lower() for alias in FIRM_CONFIGS[key].get("aliases", []))
        ]
    else:
        matched_firms = firm_keys
    if not matched_firms:
        st.warning("No configured firm matched that search. Showing the full list instead.")
        matched_firms = firm_keys
    selected_firm = st.selectbox(
        "Target account",
        matched_firms,
        format_func=lambda key: FIRM_CONFIGS[key]["name"],
    )
    firm = FIRM_CONFIGS[selected_firm]

    pages = [
        "Command Center",
        "Portfolio",
        "Leadership",
        "Hiring & Skills",
        "Technology Signals",
        "Newsroom",
        "Opportunity Lab",
        "AI Analyst",
        "Data Hub",
    ]
    if st.session_state.page not in pages:
        st.session_state.page = "Command Center"
    page = st.radio(
        "Workspace",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed",
    )
    st.session_state.page = page

    st.markdown("---")
    st.caption("PUBLIC SOURCES")
    st.markdown(f"{badge('Official websites', 'green')} {badge('Google News', 'blue')}", unsafe_allow_html=True)
    st.caption("Upload PitchBook / internal extracts in Data Hub for complete account coverage.")


# =============================================================================
# LOAD DATA — layered: upload > local file > public source
# =============================================================================
with st.spinner(f"Refreshing {firm['name']} intelligence…"):
    local_portfolio = load_local_portfolio(selected_firm)
    public_portfolio, public_portfolio_label = get_public_portfolio(selected_firm)
    portfolio = st.session_state.uploaded_portfolio.get(selected_firm) or local_portfolio or public_portfolio

    local_jobs = load_local_jobs(selected_firm)
    public_jobs = get_public_jobs(selected_firm)
    jobs = st.session_state.uploaded_jobs.get(selected_firm) or local_jobs or public_jobs

    local_leadership = load_local_leadership(selected_firm)
    public_leadership = get_public_leadership(selected_firm, full=(page == "Leadership"))
    leadership = st.session_state.uploaded_leadership.get(selected_firm) or local_leadership or public_leadership

    local_insights = load_local_insights(selected_firm)
    google_news = get_google_news(
        f'"{firm["name"]}" (private equity OR acquisition OR portfolio OR AI OR technology OR digital OR hiring)',
        limit=22,
    )
    official_news = []
    for news_url in firm.get("news_urls", [])[:2]:
        official_news.extend(get_official_news_cards(news_url, limit=12))
    uploaded_insights = st.session_state.uploaded_insights.get(selected_firm) or []
    insights = merge_insights(uploaded_insights, local_insights, google_news, official_news)

    official_bio = get_official_description(firm.get("about_url") or firm["website"])
    wiki_bio = get_wikipedia_summary(firm.get("wikipedia", firm["name"]))
    bio_record = official_bio or wiki_bio or {}
    bio_text = bio_record.get("extract", "")

capabilities = load_capabilities()
tech_rows = detect_technology_signals(jobs, insights)
why_now = build_why_now(jobs, insights, tech_rows)
opportunities = map_ai_opportunities(capabilities, tech_rows, jobs, insights, portfolio, leadership)
priority_score = compute_opportunity_score(portfolio, jobs, insights, tech_rows, leadership)
priority_band, priority_note = score_band(priority_score)
confidence_score, confidence_components = compute_data_confidence(portfolio, jobs, insights, leadership)
portfolio_mode = source_mode("uploaded_portfolio", selected_firm, local_portfolio, public_portfolio, public_portfolio_label)
jobs_mode = source_mode("uploaded_jobs", selected_firm, local_jobs, public_jobs, "Official careers scan")
leadership_mode = source_mode("uploaded_leadership", selected_firm, local_leadership, public_leadership, "Official people directory")
coverage = source_coverage(portfolio, jobs, insights, leadership, portfolio_mode, jobs_mode, leadership_mode)

hero(firm, priority_score, confidence_score, len(insights))


# =============================================================================
# COMMAND CENTER
# =============================================================================
if page == "Command Center":
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Account priority", f"{priority_score}/100", priority_band)
    with c2:
        kpi_card("Portfolio / investments", len(portfolio), portfolio_mode)
    with c3:
        kpi_card("Priority leaders", sum(1 for p in leadership if p.get("Coforge Relevance", 1) >= 4), f"{len(leadership)} people captured")
    with c4:
        kpi_card("Relevant hiring", sum(1 for j in jobs if job_relevance(j.get("title", ""), j.get("description", "")) >= 3), f"{len(jobs)} roles scanned")
    with c5:
        kpi_card("Tech themes", len(tech_rows), f"{len(insights)} recent intelligence items")

    st.write("")
    left, right = st.columns([1.36, 1], gap="large")

    with left:
        section_title("Account snapshot", "A concise view of who the firm is and why Coforge should care.", "Account")
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="card-title">{escape(firm['name'])}</div>
                <div class="card-copy">{escape(bio_text or 'A public company description could not be retrieved. The rest of the workspace remains available and can be enriched from Data Hub.')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        b1, b2, b3 = st.columns(3)
        with b1:
            st.link_button("Firm website ↗", firm["website"], use_container_width=True)
        with b2:
            st.link_button("Portfolio source ↗", firm["portfolio_urls"][0], use_container_width=True)
        with b3:
            st.link_button("People source ↗", firm["people_urls"][0], use_container_width=True)

        st.write("")
        section_title("Why now?", "Signals that can create a credible reason to approach the account now rather than later.", "Buying signals")
        if why_now:
            for item in why_now[:5]:
                st.markdown(
                    f"""
                    <div class="signal-card">
                        <div class="signal-top"><div class="signal-name">{escape(item['Signal'])}</div><div>{strength_badge(item['Strength'])}</div></div>
                        <div class="signal-copy">{escape(item['Evidence'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty-state">No strong near-term trigger is proven yet. Add job data, PitchBook portfolio data or internal account research in Data Hub.</div>', unsafe_allow_html=True)

    with right:
        section_title("Intelligence confidence", "How complete the current evidence base is across the four core data layers.", "Coverage")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence_score,
            number={"suffix": "%", "font": {"size": 34}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0},
                "bar": {"color": "#635bff"},
                "bgcolor": "#eef2ff",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#f8fafc"},
                    {"range": [40, 70], "color": "#f3f4ff"},
                    {"range": [70, 100], "color": "#eef2ff"},
                ],
            },
        ))
        gauge.update_layout(height=220, margin=dict(l=18, r=18, t=18, b=6), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for row in coverage:
            dot = "🟢" if row["Ready"] else "⚪"
            st.markdown(
                f'<div class="data-row"><div><div class="data-label">{dot} {escape(row["Layer"])}</div><div class="data-meta">{escape(row["Mode"])}</div></div><div class="data-label">{row["Records"]}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        section_title("Top AI opportunities", "Only the currently loaded Coforge capability set is used — the model will broaden as you add capabilities.", "Coforge")
        for opp in opportunities[:3]:
            st.markdown(
                f"""
                <div class="op-card" style="margin-bottom:.55rem">
                    <div class="op-head"><div class="op-name">{escape(opp['Coforge Capability'])}</div>{strength_badge(opp['Evidence Strength'])}</div>
                    <div class="op-copy">{escape(opp['Opportunity'])}</div>
                    <div class="op-evidence">{escape(opp['Evidence'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    section_title("Latest account intelligence", "Most recent public news and official-site signals available to the account workspace.", "Live feed")
    if insights:
        cols = st.columns(3)
        for idx, article in enumerate(insights[:6]):
            with cols[idx % 3]:
                display_news_card(article, compact=True)
    else:
        st.info("No recent intelligence could be loaded from public sources.")

    st.write("")
    section_title("Jump into research", kicker="Workspace")
    n1, n2, n3, n4, n5 = st.columns(5)
    with n1:
        nav_button("Portfolio →", "Portfolio", "nav_portfolio")
    with n2:
        nav_button("Leadership →", "Leadership", "nav_leadership")
    with n3:
        nav_button("Hiring →", "Hiring & Skills", "nav_hiring")
    with n4:
        nav_button("Opportunity lab →", "Opportunity Lab", "nav_opp")
    with n5:
        nav_button("Ask AI →", "AI Analyst", "nav_ai")


# =============================================================================
# PORTFOLIO
# =============================================================================
elif page == "Portfolio":
    section_title("Portfolio intelligence", "Search, segment and inspect the public portfolio/investment universe. PitchBook exports override public scraping when uploaded.", "Portfolio")
    st.markdown(f'<div class="scope-note"><b>Scope:</b> {escape(firm.get("portfolio_scope", ""))}</div>', unsafe_allow_html=True)

    if not portfolio:
        st.markdown(
            '<div class="empty-state"><b>No company-level portfolio list is currently available from the public source.</b><br>That does not mean the firm has no portfolio. For firms such as Blackstone, Apollo, Coller or Gresham House the public website may not expose a directly comparable exhaustive list. Upload a PitchBook CSV/XLSX in Data Hub.</div>',
            unsafe_allow_html=True,
        )
        st.link_button("Open official portfolio / investments page ↗", firm["portfolio_urls"][0])
    else:
        df = pd.DataFrame(portfolio)
        for col in ["Company", "Sector", "Region", "Status", "Fund", "Source"]:
            if col not in df.columns:
                df[col] = ""
        df = df.fillna("")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Records captured", len(df))
        m2.metric("Sectors", df.loc[df["Sector"].astype(bool), "Sector"].nunique())
        m3.metric("Regions", df.loc[df["Region"].astype(bool), "Region"].nunique())
        m4.metric("Source mode", portfolio_mode)

        f1, f2, f3, f4 = st.columns([1.8, 1, 1, 1])
        with f1:
            query = st.text_input("Search portfolio", placeholder="Type a company, sector, region or fund")
        with f2:
            sectors = safe_unique(df["Sector"])
            selected_sector = st.selectbox("Sector", ["All"] + sectors)
        with f3:
            regions = safe_unique(df["Region"])
            selected_region = st.selectbox("Region", ["All"] + regions)
        with f4:
            statuses = safe_unique(df["Status"])
            selected_status = st.selectbox("Status", ["All"] + statuses)

        filtered = df.copy()
        if query:
            mask = filtered.astype(str).apply(lambda c: c.str.contains(query, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
        if selected_sector != "All":
            filtered = filtered[filtered["Sector"] == selected_sector]
        if selected_region != "All":
            filtered = filtered[filtered["Region"] == selected_region]
        if selected_status != "All":
            filtered = filtered[filtered["Status"] == selected_status]

        left, right = st.columns([1.85, 1], gap="large")
        with left:
            st.dataframe(
                filtered[["Company", "Sector", "Region", "Status", "Fund"]],
                use_container_width=True,
                hide_index=True,
                height=540,
            )
            st.download_button(
                "Download filtered portfolio CSV",
                filtered.to_csv(index=False).encode("utf-8"),
                file_name=f"{selected_firm}_portfolio.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with right:
            section_title("Portfolio mix", "Based only on records with a usable sector/region label.")
            sector_counts = filtered[filtered["Sector"].astype(bool)]["Sector"].value_counts().head(9).reset_index()
            sector_counts.columns = ["Sector", "Count"]
            if not sector_counts.empty:
                fig = px.bar(sector_counts.sort_values("Count"), x="Count", y="Sector", orientation="h", text="Count")
                fig.update_layout(height=300, margin=dict(l=0, r=6, t=10, b=0), xaxis_title=None, yaxis_title=None, showlegend=False)
                fig.update_traces(marker_color="#635bff")
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            region_counts = filtered[filtered["Region"].astype(bool)]["Region"].value_counts().head(8).reset_index()
            region_counts.columns = ["Region", "Count"]
            if not region_counts.empty:
                fig2 = px.pie(region_counts, names="Region", values="Count", hole=.62)
                fig2.update_layout(height=290, margin=dict(l=0, r=0, t=8, b=0), legend_title=None)
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.divider()
        section_title("Quick company research", "Select any captured portfolio company to get a lightweight bio and recent public news without leaving the account workspace.", "Portco explorer")
        company_choices = safe_unique(filtered["Company"])
        if company_choices:
            chosen = st.selectbox("Inspect portfolio company", company_choices)
            p1, p2 = st.columns([1.15, 1], gap="large")
            with p1:
                quick_bio = get_wikipedia_summary(chosen)
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div class="card-title">{escape(chosen)}</div>
                        <div class="card-copy">{escape((quick_bio or {}).get('extract') or 'No Wikipedia company summary was found. Use the source link from the portfolio record or add richer PitchBook fields in Data Hub.')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if quick_bio and quick_bio.get("url"):
                    st.link_button("Background source ↗", quick_bio["url"])
            with p2:
                portco_news = get_google_news(f'"{chosen}" company', limit=5)
                for article in portco_news[:4]:
                    display_news_card(article, compact=True)


# =============================================================================
# LEADERSHIP
# =============================================================================
elif page == "Leadership":
    section_title("Leadership & stakeholder intelligence", "Official people directories are scanned where possible. Click a person's name to inspect their role, Coforge relevance and official-site bio.", "People")

    if not leadership:
        st.markdown('<div class="empty-state"><b>No named people were parsed from the public directory.</b><br>Upload a PitchBook/LinkedIn/official-site leadership CSV, XLSX or JSON in Data Hub. The page will automatically become interactive.</div>', unsafe_allow_html=True)
        st.link_button("Open official people directory ↗", firm["people_urls"][0])
    else:
        ldf = pd.DataFrame(leadership).fillna("")
        top_relevant = ldf.sort_values("Coforge Relevance", ascending=False)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("People captured", len(ldf))
        p2.metric("High Coforge relevance", int((ldf["Coforge Relevance"] >= 4).sum()))
        p3.metric("Roles represented", ldf.loc[ldf["Role"].astype(bool), "Role"].nunique())
        p4.metric("Source", leadership_mode)

        f1, f2, f3 = st.columns([1.7, 1, 1])
        with f1:
            q = st.text_input("Search people", placeholder="Name, CIO, operating partner, data, London…")
        with f2:
            min_rel = st.select_slider("Minimum Coforge relevance", options=[1, 2, 3, 4, 5], value=1)
        with f3:
            location_choices = safe_unique(ldf["Location"])
            loc = st.selectbox("Location", ["All"] + location_choices)

        shown = ldf[ldf["Coforge Relevance"] >= min_rel].copy()
        if q:
            mask = shown.astype(str).apply(lambda c: c.str.contains(q, case=False, na=False)).any(axis=1)
            shown = shown[mask]
        if loc != "All":
            shown = shown[shown["Location"] == loc]
        shown = shown.sort_values(["Coforge Relevance", "Name"], ascending=[False, True])

        # Searchable select is the fastest way to access hundreds of people; buttons below make names click-like.
        selected_name = st.selectbox("Jump to a person", shown["Name"].tolist() if not shown.empty else ["No matches"])
        if selected_name != "No matches":
            selected_row = shown[shown["Name"] == selected_name].iloc[0].to_dict()
            st.session_state.selected_person[selected_firm] = selected_row

        chosen_person = st.session_state.selected_person.get(selected_firm)
        if chosen_person:
            profile = get_profile_bio(chosen_person.get("Profile URL", "")) if chosen_person.get("Profile URL") else None
            bio = (profile or {}).get("bio") or chosen_person.get("Bio") or "A longer official biography was not available from the parsed source."
            st.markdown(
                f"""
                <div class="person-detail">
                    <div class="person-name">{escape(chosen_person.get('Name',''))}</div>
                    <div class="person-role">{escape(chosen_person.get('Role','Role not parsed'))}</div>
                    <div>{relevance_badge(int(chosen_person.get('Coforge Relevance',1)))} {badge(leader_reason(chosen_person.get('Role','')), 'gray')}</div>
                    <div class="person-bio" style="margin-top:.55rem">{escape(bio[:1800])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if chosen_person.get("Profile URL"):
                st.link_button("Open official profile ↗", chosen_person["Profile URL"])

        st.write("")
        section_title("People directory", "Showing the most relevant people first. Use search/filter controls for the full captured directory.")
        if shown.empty:
            st.info("No people match the current filters.")
        else:
            page_size = 24
            max_page = max(1, math.ceil(len(shown) / page_size))
            page_no = st.number_input("Directory page", min_value=1, max_value=max_page, value=1, step=1)
            start = (page_no - 1) * page_size
            subset = shown.iloc[start:start + page_size]
            cols = st.columns(3)
            for idx, (_, person) in enumerate(subset.iterrows()):
                with cols[idx % 3]:
                    st.markdown(
                        f"<div style='font-size:.72rem;color:#64748b;margin-bottom:.1rem'>{escape(person.get('Role') or 'Role not parsed')}</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button(person["Name"], key=f"person_{selected_firm}_{start+idx}", use_container_width=True):
                        st.session_state.selected_person[selected_firm] = person.to_dict()
                        st.rerun()
                    st.markdown(relevance_badge(int(person.get("Coforge Relevance", 1))), unsafe_allow_html=True)

            st.caption(f"Showing {start + 1}-{min(start + page_size, len(shown))} of {len(shown)} filtered people · page {page_no}/{max_page}")

        st.download_button(
            "Download leadership CSV",
            shown.to_csv(index=False).encode("utf-8"),
            file_name=f"{selected_firm}_leadership.csv",
            mime="text/csv",
        )


# =============================================================================
# HIRING & SKILLS
# =============================================================================
elif page == "Hiring & Skills":
    section_title("Hiring & skills intelligence", "Job openings are treated as capability-demand signals. The platform maps each role to skills Coforge could potentially support.", "Talent signals")

    if not jobs:
        st.markdown('<div class="empty-state"><b>No current job records were discovered from the configured public careers source.</b><br>This can mean there are genuinely no openings, the careers site is JavaScript/Workday-heavy, or the public scanner cannot see them. Upload a jobs export in Data Hub for complete analysis.</div>', unsafe_allow_html=True)
        if firm.get("careers_urls"):
            st.link_button("Open careers source ↗", firm["careers_urls"][0])
    else:
        enriched_rows = []
        for job in jobs:
            row = dict(job)
            row["Coforge relevance"] = job_relevance(job.get("title", ""), job.get("description", ""))
            row["Relevant skills"] = ", ".join(skills_relevant_to_coforge(job))
            enriched_rows.append(row)
        jdf = pd.DataFrame(enriched_rows).fillna("")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Roles captured", len(jdf))
        c2.metric("High relevance", int((jdf["Coforge relevance"] >= 4).sum()))
        c3.metric("Locations", jdf.loc[jdf["location"].astype(bool), "location"].nunique())
        c4.metric("Source", jobs_mode)

        f1, f2 = st.columns([2, 1])
        with f1:
            q = st.text_input("Search jobs", placeholder="AI, data, cloud, product, London…")
        with f2:
            min_job_rel = st.select_slider("Minimum Coforge relevance", options=[1, 2, 3, 4, 5], value=1)

        shown = jdf[jdf["Coforge relevance"] >= min_job_rel].copy()
        if q:
            mask = shown.astype(str).apply(lambda c: c.str.contains(q, case=False, na=False)).any(axis=1)
            shown = shown[mask]
        shown = shown.sort_values(["Coforge relevance", "title"], ascending=[False, True])

        left, right = st.columns([1.45, 1], gap="large")
        with left:
            st.dataframe(
                shown[["title", "location", "Coforge relevance", "Relevant skills", "source"]],
                use_container_width=True,
                hide_index=True,
                height=560,
                column_config={
                    "Coforge relevance": st.column_config.ProgressColumn("Coforge relevance", min_value=0, max_value=5, format="%d / 5"),
                },
            )
        with right:
            section_title("Inspect a role", "See the job evidence and the skills that create a potential Coforge conversation.")
            if not shown.empty:
                labels = [f"{r['title']} · {r['location']}".strip(" ·") for _, r in shown.head(100).iterrows()]
                selected_label = st.selectbox("Role", labels)
                chosen_idx = labels.index(selected_label)
                job = shown.iloc[chosen_idx].to_dict()
                full_description = job.get("description", "")
                if len(full_description) < 250 and job.get("url"):
                    fetched = enrich_job_description(job["url"])
                    if fetched:
                        full_description = fetched
                skills = extract_skills(f"{job.get('title','')} {full_description}")
                relevance = job_relevance(job.get("title", ""), full_description)
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div class="card-title">{escape(job.get('title',''))}</div>
                        <div>{relevance_badge(relevance)}</div>
                        <div class="card-copy" style="margin-top:.45rem">{escape((full_description or 'No job-description text was available from the public source.')[:1600])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(" ".join(badge(x, "purple") for x in skills[:10]) if skills else badge("No mapped Coforge-relevant skills", "gray"), unsafe_allow_html=True)
                if relevance >= 4:
                    st.success("Strong signal: this role suggests a technology/data/AI capability requirement worth validating with the account.")
                elif relevance >= 3:
                    st.info("Moderate signal: potentially relevant, but the exact Coforge angle needs qualification.")
                if job.get("url"):
                    st.link_button("Open job source ↗", job["url"], use_container_width=True)
            else:
                st.info("No roles match the current filters.")

        st.divider()
        section_title("Skill demand map", "Frequency of Coforge-relevant skills across captured role titles and descriptions.", "Demand")
        skill_counts = {}
        for job in jobs:
            for skill in skills_relevant_to_coforge(job):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        if skill_counts:
            sdf = pd.DataFrame([{"Skill": k, "Roles": v} for k, v in skill_counts.items()]).sort_values("Roles", ascending=True)
            fig = px.bar(sdf.tail(14), x="Roles", y="Skill", orientation="h", text="Roles")
            fig.update_traces(marker_color="#635bff")
            fig.update_layout(height=430, margin=dict(l=0, r=8, t=10, b=0), xaxis_title=None, yaxis_title=None, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
# TECHNOLOGY SIGNALS
# =============================================================================
elif page == "Technology Signals":
    section_title("Technology signal engine", "Signals are inferred from job titles/descriptions plus recent company/news intelligence. Mentions are evidence of interest or activity — not proof of enterprise-wide adoption.", "Technology")

    if not tech_rows:
        st.markdown('<div class="empty-state">No technology keywords were detected in the current evidence base. Upload richer job descriptions or internal insights in Data Hub.</div>', unsafe_allow_html=True)
    else:
        tdf = pd.DataFrame(tech_rows)
        top = tdf.head(12)
        cols = st.columns(4)
        for idx, (_, row) in enumerate(top.head(8).iterrows()):
            with cols[idx % 4]:
                kpi_card(row["Technology"], row["Mentions"], f"Jobs {row['Job Evidence']} · News {row['News Evidence']}")

        st.write("")
        left, right = st.columns([1.15, 1.5], gap="large")
        with left:
            fig = px.bar(top.sort_values("Mentions"), x="Mentions", y="Technology", orientation="h", text="Mentions")
            fig.update_traces(marker_color="#635bff")
            fig.update_layout(height=455, margin=dict(l=0, r=8, t=10, b=0), xaxis_title=None, yaxis_title=None, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with right:
            selected_tech = st.selectbox("Inspect supporting evidence", tdf["Technology"].tolist())
            evidence = tech_evidence(selected_tech, jobs, insights, max_items=7)
            if evidence:
                for item in evidence:
                    st.markdown(
                        f"""
                        <div class="signal-card">
                            <div class="signal-top"><div class="signal-name">{escape(item['title'])}</div><div>{badge(item['type'], 'gray')}</div></div>
                            <div class="signal-copy">{escape(item.get('copy') or 'Signal detected in source title.')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if item.get("url"):
                        st.link_button("Evidence source ↗", item["url"])
            else:
                st.info("The term exists in the aggregate corpus, but a short display extract could not be isolated.")

        st.markdown(" ".join(badge(x["Technology"], "purple") for x in tech_rows[:18]), unsafe_allow_html=True)


# =============================================================================
# NEWSROOM
# =============================================================================
elif page == "Newsroom":
    section_title("Latest news & growth intelligence", "Combines Google News with parsable official-site news/insights and any internal dataset you upload.", "Newsroom")

    if not insights:
        st.warning("No recent intelligence is available right now.")
    else:
        signal_types = safe_unique([x.get("signal_type", "Other") for x in insights])
        f1, f2, f3 = st.columns([1.7, 1, 1])
        with f1:
            q = st.text_input("Search intelligence", placeholder="AI, acquisition, fund, portfolio company…")
        with f2:
            signal_filter = st.selectbox("Signal type", ["All"] + signal_types)
        with f3:
            source_filter = st.selectbox("Source", ["All"] + safe_unique([x.get("source", "") for x in insights]))

        shown = insights
        if q:
            ql = q.lower()
            shown = [x for x in shown if ql in f"{x.get('title','')} {x.get('summary','')}".lower()]
        if signal_filter != "All":
            shown = [x for x in shown if x.get("signal_type") == signal_filter]
        if source_filter != "All":
            shown = [x for x in shown if x.get("source") == source_filter]

        # Signal overview
        counts = pd.Series([x.get("signal_type", "Other") for x in shown]).value_counts().reset_index()
        counts.columns = ["Signal", "Count"]
        if not counts.empty:
            fig = px.bar(counts.sort_values("Count"), x="Count", y="Signal", orientation="h", text="Count")
            fig.update_traces(marker_color="#635bff")
            fig.update_layout(height=310, margin=dict(l=0, r=8, t=8, b=0), xaxis_title=None, yaxis_title=None, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.caption(f"Showing {min(len(shown), 30)} of {len(shown)} matching intelligence items")
        cols = st.columns(2)
        for idx, article in enumerate(shown[:30]):
            with cols[idx % 2]:
                display_news_card(article)


# =============================================================================
# OPPORTUNITY LAB
# =============================================================================
elif page == "Opportunity Lab":
    section_title("Coforge opportunity lab", "Ranks the account using evidence, explains the score and maps only the Coforge capabilities currently loaded in the platform.", "Opportunity")

    score_left, score_right = st.columns([1, 2.3], gap="large")
    with score_left:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="kpi-label">Composite priority score</div>
                <div class="score-number">{priority_score}<span style="font-size:1rem;color:#94a3b8">/100</span></div>
                <div>{priority_badge(priority_score)}</div>
                <div class="card-copy" style="margin-top:.55rem">{escape(priority_note)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Prioritisation heuristic only — not a forecast of sales value or purchase intent.")
    with score_right:
        breakdown = opportunity_score_breakdown(portfolio, jobs, insights, tech_rows, leadership)
        bdf = pd.DataFrame([{"Component": k, "Points": v} for k, v in breakdown.items()])
        fig = px.bar(bdf, x="Points", y="Component", orientation="h", text="Points")
        fig.update_traces(marker_color="#635bff")
        fig.update_layout(height=330, margin=dict(l=0, r=8, t=8, b=0), xaxis_title="Points toward score", yaxis_title=None, showlegend=False, xaxis_range=[0, 35])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.write("")
    section_title("Recommended AI account plays", "Each opportunity shows the underlying evidence and the best buyer identified from the leadership directory.")
    if opportunities:
        cols = st.columns(2)
        for idx, opp in enumerate(opportunities[:8]):
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div class="op-card">
                        <div class="op-head"><div class="op-name">{escape(opp['Coforge Capability'])}</div>{strength_badge(opp['Evidence Strength'])}</div>
                        <div class="op-copy">{escape(opp['Opportunity'])}</div>
                        <div class="op-evidence"><b>Evidence:</b> {escape(opp['Evidence'])}<br><b>Suggested buyer:</b> {escape(opp['Recommended Buyer'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.write("")
    else:
        st.info("There is not enough evidence to create a credible AI opportunity map yet.")

    st.divider()
    section_title("Current Coforge capability library", "This is deliberately editable. Replace or extend the JSON in Data Hub as you get more Coforge capability material.", "Capability model")
    cap_df = pd.DataFrame(capabilities)
    st.dataframe(cap_df, use_container_width=True, hide_index=True)

    st.divider()
    section_title("Account briefing pack", "Download a portable Markdown brief containing the current evidence, priority people, jobs, signals and recommended AI angles.", "Export")
    brief = make_account_brief_markdown(
        firm, bio_text, priority_score, priority_band, portfolio, leadership, jobs, insights, tech_rows, why_now, opportunities, coverage
    )
    st.download_button(
        "Download account briefing (.md)",
        brief,
        file_name=f"{selected_firm}_coforge_account_brief.md",
        mime="text/markdown",
        type="primary",
    )


# =============================================================================
# AI ANALYST
# =============================================================================
elif page == "AI Analyst":
    section_title("AI account analyst", "Ask evidence-grounded questions across portfolio, people, jobs, technology, news and the current Coforge AI capability library.", "Research copilot")

    a1, a2 = st.columns([1.5, 1], gap="large")
    with a1:
        quick_prompts = [
            "What are the top 3 AI opportunities for Coforge at this firm and what evidence supports each one?",
            "Who are the 5 people Coforge should approach first, and why?",
            "What technology and hiring signals suggest active transformation?",
            "Create a concise pre-meeting brief for a Coforge account executive.",
            "What evidence is missing before we should treat this account as qualified?",
        ]
        preset = st.selectbox("Suggested analysis", ["Write my own question"] + quick_prompts)
        question = st.text_area(
            "Ask the analyst",
            value="" if preset == "Write my own question" else preset,
            placeholder="Example: What is the strongest evidence that this firm could need AI engineering support?",
            height=130,
        )
        model_name = st.text_input("Local Ollama model", value="gemma3", help="Optional. If unavailable, the app uses its deterministic signal engine instead.")

        context = build_ai_context(
            firm["name"], bio_text, jobs, insights, portfolio, tech_rows, opportunities, leadership, why_now, capabilities
        )
        if st.button("Run account analysis", type="primary", use_container_width=True):
            if not question.strip():
                st.warning("Enter a question first.")
            else:
                with st.spinner("Synthesising evidence across the account…"):
                    answer, engine = run_ai_analysis(
                        question,
                        firm["name"],
                        context,
                        model_name,
                        priority_score,
                        tech_rows,
                        opportunities,
                        jobs,
                        insights,
                        portfolio,
                        leadership,
                        why_now,
                    )
                st.session_state.analysis_history.insert(0, {
                    "firm": firm["name"],
                    "question": question,
                    "answer": answer,
                    "engine": engine,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.success(f"Analysis complete · {engine}")
                st.markdown(answer)
                st.download_button(
                    "Download analysis",
                    answer,
                    file_name=f"{selected_firm}_ai_analysis.md",
                    mime="text/markdown",
                )

    with a2:
        section_title("Analyst context", "What the AI is actually allowed to see for this account.")
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="data-row"><div class="data-label">Portfolio / investments</div><div class="data-label">{len(portfolio)}</div></div>
                <div class="data-row"><div class="data-label">Leadership people</div><div class="data-label">{len(leadership)}</div></div>
                <div class="data-row"><div class="data-label">Hiring records</div><div class="data-label">{len(jobs)}</div></div>
                <div class="data-row"><div class="data-label">News / insights</div><div class="data-label">{len(insights)}</div></div>
                <div class="data-row"><div class="data-label">Technology themes</div><div class="data-label">{len(tech_rows)}</div></div>
                <div class="data-row"><div class="data-label">Coforge capabilities</div><div class="data-label">{len(capabilities)}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("The system prompt explicitly tells the analyst not to invent people, portfolio companies, technologies or initiatives, and to flag missing evidence.")

        if st.session_state.analysis_history:
            section_title("Recent analyses")
            for item in st.session_state.analysis_history[:4]:
                with st.expander(f"{item['firm']} · {item['question'][:65]}"):
                    st.caption(f"{item['timestamp']} · {item['engine']}")
                    st.markdown(item["answer"])


# =============================================================================
# DATA HUB
# =============================================================================
elif page == "Data Hub":
    section_title("Data hub & source control", "This is where public web intelligence becomes an internal Coforge-grade account dataset. Upload PitchBook exports or curated research; uploads override public extraction for the current session.", "Data")

    rows = pd.DataFrame(coverage)
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.write("")
    st.markdown(f'<div class="scope-note"><b>Portfolio scope for {escape(firm["name"])}:</b> {escape(firm.get("portfolio_scope", ""))}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Portfolio", "Leadership", "Jobs", "News / Insights", "Coforge capabilities"])

    with tab1:
        section_title("Upload portfolio / investments", "Accepted: CSV, XLSX or JSON. PitchBook exports are ideal; common column names are normalized automatically.")
        up = st.file_uploader("Portfolio file", type=["csv", "xlsx", "json"], key=f"port_{selected_firm}")
        if up is not None:
            parsed = normalize_portfolio(parse_uploaded_file(up))
            if parsed:
                st.session_state.uploaded_portfolio[selected_firm] = parsed
                st.success(f"Loaded {len(parsed)} portfolio/investment records. Public data is now overridden for this session.")
                st.dataframe(pd.DataFrame(parsed).head(20), use_container_width=True, hide_index=True)
            else:
                st.error("The file was read but no recognizable portfolio records were found.")
        st.caption("Recommended columns: Company, Sector, Region, Status, Fund, Source")

    with tab2:
        section_title("Upload leadership", "Use a complete people export when you need certainty beyond the official-site parser.")
        up = st.file_uploader("Leadership file", type=["csv", "xlsx", "json"], key=f"lead_{selected_firm}")
        if up is not None:
            parsed = normalize_leadership(parse_uploaded_file(up))
            if parsed:
                st.session_state.uploaded_leadership[selected_firm] = parsed
                st.success(f"Loaded {len(parsed)} people. The Leadership page is now using this dataset.")
                st.dataframe(pd.DataFrame(parsed).head(20), use_container_width=True, hide_index=True)
            else:
                st.error("No recognizable leadership records were found.")
        st.caption("Recommended columns: Name, Role, Location, Bio, Profile URL, Source")

    with tab3:
        section_title("Upload hiring data", "Best results come from job title + location + full description + source URL.")
        up = st.file_uploader("Jobs file", type=["csv", "xlsx", "json"], key=f"jobs_{selected_firm}")
        if up is not None:
            parsed = normalize_jobs(parse_uploaded_file(up))
            if parsed:
                st.session_state.uploaded_jobs[selected_firm] = parsed
                st.success(f"Loaded {len(parsed)} jobs. Technology and skill signals update immediately.")
                st.dataframe(pd.DataFrame(parsed).head(20), use_container_width=True, hide_index=True)
            else:
                st.error("No recognizable job records were found.")
        st.caption("Recommended columns: title, location, description, url")

    with tab4:
        section_title("Upload internal news / insights", "Add curated account research, official insights or internal Coforge observations alongside the live public feed.")
        up = st.file_uploader("Insights file", type=["csv", "xlsx", "json"], key=f"ins_{selected_firm}")
        if up is not None:
            parsed = normalize_insights(parse_uploaded_file(up))
            if parsed:
                st.session_state.uploaded_insights[selected_firm] = parsed
                st.success(f"Loaded {len(parsed)} insight records. These are merged with live news rather than replacing it.")
                st.dataframe(pd.DataFrame(parsed).head(20), use_container_width=True, hide_index=True)
            else:
                st.error("No recognizable insight records were found.")
        st.caption("Recommended columns: title, summary, link, published, source, signal_type")

    with tab5:
        section_title("Coforge capability model", "The app currently ships with an AI-focused starter library. Edit data/coforge_capabilities.json to add verified Coforge offerings later.")
        st.dataframe(pd.DataFrame(capabilities), use_container_width=True, hide_index=True)
        st.code(
            '[\n  {\n    "Capability": "AI & Generative AI",\n    "Description": "...",\n    "Signal Keywords": ["genai", "llm", "machine learning"]\n  }\n]',
            language="json",
        )

    st.divider()
    section_title("Persistent local data folders", "For repeatable use, save datasets beside the app instead of re-uploading them every session.", "Developer")
    st.code(
        f"""data/
  {selected_firm}/
    portfolio.csv   # or .xlsx / .json
    leadership.csv
    jobs.csv
    insights.csv
  coforge_capabilities.json""",
        language="text",
    )
    st.caption("The app automatically detects these files on startup. Session uploads take precedence over local files, which take precedence over public web extraction.")

    st.write("")
    if st.button("Clear session uploads for this firm"):
        for key in ["uploaded_portfolio", "uploaded_jobs", "uploaded_insights", "uploaded_leadership"]:
            st.session_state[key].pop(selected_firm, None)
        st.success("Session overrides cleared. Reload the page to return to local/public sources.")
