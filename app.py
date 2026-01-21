"""
EAI DealFlow Terminal - Main Streamlit Application
AI-powered deal sourcing and valuation platform for M&A analysts.
"""

import streamlit as st
from modules.data_ingestion import load_all_csvs, get_peer_group, get_available_industries
from modules.scoring import calculate_deal_heat, get_heat_color, get_heat_label
from modules.visualization import create_market_chart, calculate_valuation_range, get_chart_config
from modules.ai_service import scrape_website_summary, generate_emails, generate_upside_bullets
from modules.pdf_generator import generate_one_pager
from modules.storage import (
    save_entry, get_all_entries, get_pdf_bytes,
    delete_entry, delete_entries, auto_archive_old_entries,
    increment_stat, get_stats
)
from modules.config import load_config, save_config, reset_to_defaults
from modules.first_visit import (
    is_first_visit, get_current_tooltip, advance_tooltip,
    skip_tour, get_tour_progress, reset_tour
)

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="EAI DealFlow Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== LOAD CONFIG AND DATA =====
config = load_config()


@st.cache_data(ttl=300)
def load_data():
    """Load and cache CSV data."""
    return load_all_csvs("data")


df = load_data()

# Auto-archive old entries on startup
auto_archive_old_entries(config.get('auto_archive_days', 90))

# ===== SESSION STATE INITIALIZATION =====
if 'target_margin' not in st.session_state:
    st.session_state.target_margin = None
if 'emails_generated' not in st.session_state:
    st.session_state.emails_generated = None
if 'website_summary' not in st.session_state:
    st.session_state.website_summary = ""

# ===== DARK THEME CSS =====
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Root variables */
    :root {
        --bg-primary: #0E1117;
        --bg-secondary: #1a1f2e;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --text-primary: #ffffff;
        --text-secondary: #9ca3af;
        --accent-blurple: #6366f1;
        --accent-cyan: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
    }

    /* Background */
    .stApp {
        background: radial-gradient(ellipse at top center, var(--bg-secondary) 0%, var(--bg-primary) 50%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.02);
        border-right: 1px solid var(--glass-border);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }

    /* Glass panels */
    .stTabs [data-baseweb="tab-panel"] {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--accent-blurple) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    .stSelectbox > div > div {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary button */
    .stButton > button[kind="secondary"], .stButton > button[data-testid="baseButton-secondary"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #06b6d4) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--success), var(--accent-cyan)) !important;
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    p, span, label, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-secondary) !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--glass-bg) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--glass-bg);
        border-radius: 8px 8px 0 0;
        color: var(--text-secondary);
        font-family: 'Inter', sans-serif;
    }

    .stTabs [aria-selected="true"] {
        background: var(--accent-blurple) !important;
        color: white !important;
    }

    /* Text area */
    .stTextArea textarea {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Divider */
    hr {
        border-color: var(--glass-border) !important;
    }

    /* Info box */
    .stAlert {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] {
        background: var(--glass-border) !important;
    }

    .stSlider [data-testid="stThumbValue"] {
        color: var(--text-primary) !important;
    }

    /* Checkbox */
    .stCheckbox label {
        color: var(--text-primary) !important;
    }

    /* Caption */
    .stCaption {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }

    /* First-visit tooltip styles */
    .tooltip-banner {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
        border: 1px solid var(--accent-blurple);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        position: relative;
        backdrop-filter: blur(8px);
    }

    .tooltip-banner-title {
        color: var(--text-primary) !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .tooltip-banner-message {
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        margin-bottom: 0.75rem !important;
    }

    .tooltip-progress {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.75rem;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }

    .tooltip-progress-dots {
        display: flex;
        gap: 4px;
    }

    .tooltip-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--glass-border);
    }

    .tooltip-dot.active {
        background: var(--accent-blurple);
    }

    .tooltip-dot.completed {
        background: var(--success);
    }
</style>
""", unsafe_allow_html=True)

# ===== FIRST VISIT TOOLTIP =====
# Initialize session state for tour
if 'tour_action' not in st.session_state:
    st.session_state.tour_action = None


def render_tooltip_banner():
    """Render the first-visit tooltip banner if applicable."""
    if not is_first_visit():
        return

    tooltip = get_current_tooltip()
    if not tooltip:
        return

    progress = get_tour_progress()

    # Icon mapping
    icon_map = {
        "wave": "\U0001F44B",
        "building": "\U0001F3E2",
        "fire": "\U0001F525",
        "chart": "\U0001F4C8",
        "email": "\U0001F4E7",
        "history": "\U0001F4CB"
    }

    icon = icon_map.get(tooltip.get("icon", ""), "\U0001F4A1")

    # Build progress dots HTML
    dots_html = ""
    for i in range(progress["total_steps"]):
        if i < progress["current_step"]:
            dots_html += '<span class="tooltip-dot completed"></span>'
        elif i == progress["current_step"]:
            dots_html += '<span class="tooltip-dot active"></span>'
        else:
            dots_html += '<span class="tooltip-dot"></span>'

    st.markdown(f"""
    <div class="tooltip-banner">
        <div class="tooltip-banner-title">{icon} {tooltip['title']}</div>
        <div class="tooltip-banner-message">{tooltip['message']}</div>
        <div class="tooltip-progress">
            <div class="tooltip-progress-dots">{dots_html}</div>
            <span>Step {progress['current_step'] + 1} of {progress['total_steps']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Next \u2192", key="tour_next", type="primary", use_container_width=True):
            st.session_state.tour_action = "next"
    with col2:
        if st.button("Skip Tour", key="tour_skip", use_container_width=True):
            st.session_state.tour_action = "skip"

    # Handle tour actions
    if st.session_state.tour_action == "next":
        st.session_state.tour_action = None
        advance_tooltip()
        st.rerun()
    elif st.session_state.tour_action == "skip":
        st.session_state.tour_action = None
        skip_tour()
        st.toast("Tour skipped. You can restart it from Admin Settings.", icon="\u2705")
        st.rerun()


# Render tooltip banner at the top of the page
render_tooltip_banner()

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("## 📊 DealFlow Terminal")
    st.caption("AI-Powered Deal Sourcing")

    st.divider()

    # Target Input Section
    st.markdown("### Target Input")

    company_name = st.text_input(
        "Company Name",
        placeholder="e.g., Bob's HVAC",
        help="Enter the target company's name"
    )

    website = st.text_input(
        "Website URL",
        placeholder="e.g., bobshvac.com",
        help="Optional: Used for AI-powered context extraction"
    )

    industries = get_available_industries(df)
    industry_options = industries + ["+ Add Custom"]
    industry = st.selectbox(
        "Industry",
        options=industry_options,
        help="Select industry or add a custom one"
    )

    if industry == "+ Add Custom":
        industry = st.text_input("Enter custom industry", placeholder="e.g., Manufacturing")

    revenue = st.number_input(
        "Revenue ($)",
        min_value=0,
        value=3_000_000,
        step=100_000,
        format="%d",
        help="Annual revenue in dollars"
    )

    tone = st.selectbox(
        "Email Tone",
        options=["Formal", "Friendly", "Direct"],
        help="Sets the communication style for generated emails"
    )

    st.divider()

    # Deal Heat Score
    if company_name and revenue > 0 and industry and industry != "+ Add Custom":
        peers = get_peer_group(df, industry, revenue)
        peer_count = len(peers)
        median_margin = peers['ebitda_margin'].median() if peer_count > 0 and 'ebitda_margin' in peers.columns else 0
        heat = calculate_deal_heat(revenue, peer_count, median_margin if median_margin else 0, config)
        color = get_heat_color(heat)
        label = get_heat_label(heat)

        st.markdown("### Deal Heat Score")
        st.markdown(
            f"<h2 style='color:{color}; margin:0; font-family: JetBrains Mono;'>{heat}/100</h2>",
            unsafe_allow_html=True
        )
        st.progress(heat / 100)
        st.caption(f"Rating: {label} | Based on {peer_count} comparable deals")

    st.divider()

    # Admin Settings (Collapsible)
    with st.expander("⚙️ Admin Settings"):
        st.markdown("#### Deal Heat Thresholds")

        dh = config.get('deal_heat', {})

        col1, col2 = st.columns(2)
        with col1:
            new_rev_min = st.number_input(
                "Rev Min ($M)",
                value=int(dh.get('revenue_min', 2_000_000) / 1_000_000),
                min_value=0,
                max_value=100,
                step=1,
                key="admin_rev_min"
            ) * 1_000_000

        with col2:
            new_rev_max = st.number_input(
                "Rev Max ($M)",
                value=int(dh.get('revenue_max', 10_000_000) / 1_000_000),
                min_value=0,
                max_value=100,
                step=1,
                key="admin_rev_max"
            ) * 1_000_000

        new_peer_thresh = st.number_input(
            "Peer Count Threshold",
            value=dh.get('peer_threshold', 5),
            min_value=1,
            max_value=20,
            key="admin_peer_thresh"
        )

        new_margin_thresh = st.number_input(
            "Margin Threshold (%)",
            value=dh.get('margin_threshold', 15),
            min_value=0,
            max_value=50,
            key="admin_margin_thresh"
        )

        st.divider()
        st.markdown("#### Archive Settings")

        new_auto_archive = st.number_input(
            "Auto-Archive After (Days)",
            value=config.get('auto_archive_days', 90),
            min_value=7,
            max_value=365,
            step=1,
            help="Entries older than this many days will be automatically archived",
            key="admin_auto_archive"
        )

        # Auto-save on change - check all settings
        settings_changed = (
            new_rev_min != dh.get('revenue_min') or
            new_rev_max != dh.get('revenue_max') or
            new_peer_thresh != dh.get('peer_threshold') or
            new_margin_thresh != dh.get('margin_threshold') or
            new_auto_archive != config.get('auto_archive_days', 90)
        )

        if settings_changed:
            # Preserve existing nested config values (weights, label_thresholds)
            updated_deal_heat = {
                **dh,
                'revenue_min': new_rev_min,
                'revenue_max': new_rev_max,
                'peer_threshold': new_peer_thresh,
                'margin_threshold': new_margin_thresh
            }
            config['deal_heat'] = updated_deal_heat
            config['auto_archive_days'] = new_auto_archive
            save_config(config)
            st.success("Settings auto-saved!")
            st.rerun()

        st.divider()

        col_reset1, col_reset2 = st.columns(2)
        with col_reset1:
            if st.button("Reset to Defaults", use_container_width=True):
                config = reset_to_defaults()
                st.rerun()
        with col_reset2:
            if st.button("Restart Tour", use_container_width=True):
                reset_tour()
                st.toast("Tour restarted!", icon="\U0001F503")
                st.rerun()

        st.divider()

        # Usage Stats
        st.markdown("#### Usage Stats")
        stats = get_stats()
        st.metric("Reports Generated", stats.get('reports_generated', 0))
        st.metric("PDFs Downloaded", stats.get('pdfs_downloaded', 0))

# ===== MAIN CONTENT =====
col1, col2 = st.columns([2, 1])

with col1:
    # Tabs for Analysis and History
    tab1, tab2 = st.tabs(["📈 Analysis", "📋 History"])

    with tab1:
        if company_name and revenue > 0 and industry and industry != "+ Add Custom":
            peers = get_peer_group(df, industry, revenue)

            # Calculate default target margin
            if st.session_state.target_margin is None:
                if len(peers) > 0 and 'ebitda_margin' in peers.columns:
                    default_margin = peers['ebitda_margin'].median()
                    initial_margin = default_margin if default_margin and default_margin > 0 else 15.0
                else:
                    initial_margin = 15.0
            else:
                initial_margin = st.session_state.target_margin

            # Real-time chart fragment - only this section re-renders on slider change
            @st.fragment
            def render_margin_chart(peers_data, target_name, target_revenue, default_margin):
                """Render slider and chart as a fragment for real-time updates."""
                target_margin = st.slider(
                    "Adjust Target Margin (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=float(default_margin),
                    step=0.5,
                    help="Drag to adjust the target's estimated EBITDA margin position",
                    key="margin_slider"
                )
                st.session_state.target_margin = target_margin

                # Create and display chart
                fig = create_market_chart(peers_data, target_name, target_revenue, target_margin)
                st.plotly_chart(fig, use_container_width=True, config=get_chart_config())

            # Call the fragment with current data
            render_margin_chart(peers, company_name, revenue, initial_margin)

            # Valuation range
            val_range = calculate_valuation_range(peers, revenue)
            if val_range[0] > 0:
                st.markdown("### Estimated Valuation Range")
                vcol1, vcol2, vcol3 = st.columns(3)
                with vcol1:
                    st.metric("Low (25th %ile)", f"${val_range[0]:,.0f}")
                with vcol2:
                    st.metric("Median", f"${val_range[2]:,.0f}")
                with vcol3:
                    st.metric("High (75th %ile)", f"${val_range[1]:,.0f}")
            else:
                st.info("No comparable transactions found for valuation estimate. Try adjusting the revenue or industry.")
        else:
            st.markdown("### Welcome to DealFlow Terminal")
            st.info("👈 Enter company details in the sidebar to begin analysis.")

            # Quick stats
            if not df.empty:
                st.markdown("#### Database Overview")
                scol1, scol2, scol3 = st.columns(3)
                with scol1:
                    st.metric("Total Transactions", len(df))
                with scol2:
                    if 'industry' in df.columns:
                        st.metric("Industries", df['industry'].nunique())
                with scol3:
                    if 'revenue' in df.columns:
                        st.metric("Avg Revenue", f"${df['revenue'].mean():,.0f}")

    with tab2:
        # History View
        st.markdown("### Report History")

        entries = get_all_entries(include_archived=False)

        if entries:
            selected_ids = []

            for entry in entries:
                with st.container():
                    ecol1, ecol2, ecol3, ecol4 = st.columns([0.5, 3, 1, 1])

                    with ecol1:
                        if st.checkbox("", key=f"select_{entry['id']}", label_visibility="collapsed"):
                            selected_ids.append(entry['id'])

                    with ecol2:
                        st.markdown(f"**{entry['company_name']}**")
                        st.caption(f"{entry['industry']} | ${entry['revenue']:,.0f} | Heat: {entry['deal_heat']}")

                    with ecol3:
                        st.caption(entry['created_at'][:10])

                    with ecol4:
                        pdf = get_pdf_bytes(entry['id'])
                        if pdf:
                            st.download_button(
                                "📄",
                                pdf,
                                f"{entry['company_name']}_Valuation.pdf",
                                key=f"pdf_{entry['id']}",
                                help="Download PDF"
                            )

                st.divider()

            if selected_ids:
                if st.button(f"🗑️ Delete Selected ({len(selected_ids)})", type="secondary"):
                    deleted = delete_entries(selected_ids)
                    st.success(f"Deleted {deleted} entries")
                    st.rerun()
        else:
            st.info("No saved reports yet. Generate your first report to see it here!")

with col2:
    st.markdown("### 📧 Outreach Strategy")

    # Generate Strategy Button
    if company_name and revenue > 0 and industry and industry != "+ Add Custom":
        if st.button("🚀 Generate Strategy", type="primary", use_container_width=True):
            with st.spinner("AI generating personalized emails..."):
                # Get website summary (silent fallback on failure)
                summary = ""
                if website:
                    summary = scrape_website_summary(website)
                    st.session_state.website_summary = summary

                # Get peer data for context
                peers = get_peer_group(df, industry, revenue)
                median_multiple = 3.0
                if len(peers) > 0 and 'multiple' in peers.columns:
                    mm = peers['multiple'].median()
                    if mm and mm > 0:
                        median_multiple = mm

                # Generate emails in parallel
                emails = generate_emails(
                    company_name,
                    industry,
                    revenue,
                    median_multiple,
                    summary,
                    tone.lower()
                )

                st.session_state.emails_generated = emails

            st.success("Strategy generated!")

        # Display generated emails
        if st.session_state.emails_generated:
            emails = st.session_state.emails_generated

            email_tabs = st.tabs(["🎣 Hook", "📎 Asset", "🤝 Close"])

            for tab, key, label in zip(email_tabs, ['hook', 'asset', 'close'], ['Hook', 'Asset', 'Close']):
                with tab:
                    email = emails.get(key, {'subject': '', 'body': ''})

                    st.text_input(
                        "Subject",
                        value=email.get('subject', ''),
                        key=f"subject_{key}",
                        disabled=True
                    )

                    st.text_area(
                        "Body",
                        value=email.get('body', ''),
                        height=200,
                        key=f"body_{key}"
                    )

                    # Copy functionality
                    full_email = f"Subject: {email.get('subject', '')}\n\n{email.get('body', '')}"
                    if st.button(f"📋 Copy {label} Email", key=f"copy_{key}", use_container_width=True):
                        st.code(full_email, language=None)
                        increment_stat("emails_copied")
                        st.info("👆 Select all text above and copy (Cmd+C)")

            st.divider()

            # PDF Generation
            if st.button("📄 Generate PDF Report", type="secondary", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    try:
                        peers = get_peer_group(df, industry, revenue)
                        target_margin = st.session_state.target_margin or 15.0
                        val_range = calculate_valuation_range(peers, revenue)

                        # Get top 3 comps
                        if len(peers) > 0:
                            top_comps = peers.nlargest(3, 'revenue') if 'revenue' in peers.columns else peers.head(3)
                        else:
                            top_comps = peers

                        # Generate upside bullets
                        peer_median = 15.0
                        if len(peers) > 0 and 'ebitda_margin' in peers.columns:
                            pm = peers['ebitda_margin'].median()
                            if pm and pm > 0:
                                peer_median = pm

                        upside = generate_upside_bullets(
                            company_name,
                            industry,
                            target_margin,
                            peer_median,
                            st.session_state.get('website_summary', '')
                        )

                        # Create chart for PDF
                        fig = create_market_chart(peers, company_name, revenue, target_margin)

                        # Generate PDF
                        pdf_bytes = generate_one_pager(
                            company_name,
                            industry,
                            revenue,
                            val_range,
                            top_comps,
                            fig,
                            upside
                        )

                        # Calculate heat score
                        heat = calculate_deal_heat(
                            revenue,
                            len(peers),
                            peer_median,
                            config
                        )

                        # Save to history
                        entry_id = save_entry(
                            company_name,
                            industry,
                            revenue,
                            website,
                            heat,
                            val_range,
                            st.session_state.emails_generated,
                            pdf_bytes
                        )

                        # Download button
                        st.download_button(
                            "⬇️ Download PDF",
                            pdf_bytes,
                            f"{company_name.replace(' ', '_')}_Valuation.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        increment_stat("pdfs_downloaded")
                        st.success(f"Report saved! (ID: {entry_id[:8]}...)")

                    except Exception as e:
                        st.error(f"PDF generation failed: {str(e)}")
    else:
        st.info("👈 Enter company details in the sidebar to generate outreach strategy.")

# ===== FOOTER =====
st.divider()
st.caption("EAI DealFlow Terminal v2.0 | Powered by Gemini AI")
