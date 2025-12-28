"""Landing Page: Fund Investigator

Professional-grade mutual fund analysis platform
"""
import streamlit as st
from pathlib import Path


def render_hero_section():
    """Render hero section with logo and headline"""

    # Construct path to logo (without tagline)
    logo_path = Path(__file__).parent.parent.parent / \
        "fundinvestigator-brand-package/brand-package-final/logo-primary.svg"

    # Hero section with Navy background
    st.markdown(f"""
        <div class="hero-section">
            <div class="logo-container">
                <img src="data:image/svg+xml;base64,{get_svg_b64(logo_path)}" alt="Fund Investigator" class="hero-logo" style="width: 350px; max-width: 90%;">
            </div>
            <h1 class="hero-headline" style="color: #FFFFFF !important;">Professional-Grade Fund Analysis</h1>
            <p class="hero-subheadline" style="color: #D4AF37 !important;">Institutional metrics and insights for every investor</p>
        </div>
    """, unsafe_allow_html=True)


def render_value_propositions():
    """Render 6 value proposition cards in 3x2 grid"""

    st.markdown('<h2 class="section-title">Why Fund Investigator?</h2>', unsafe_allow_html=True)

    values = [
        ("📊", "30+ Performance Metrics", "CAGR, Sharpe, Sortino, Alpha, Beta, and more"),
        ("💰", "SIP Analysis with IRR", "Track systematic investment plan performance"),
        ("⚖️", "Benchmark Comparison", "Side-by-side analysis vs indices"),
        ("☁️", "Real-time Data from R2", "Always current with daily NAV updates"),
        ("📈", "Interactive Visualizations", "Plotly charts with drill-down capabilities"),
        ("🔄", "Rolling Metrics", "Time-based windows (6M, 1Y, 3Y, 5Y)"),
    ]

    # Render in 3 columns, 2 rows
    for i in range(0, 6, 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(values):
                icon, title, description = values[i + j]
                with col:
                    st.markdown(f"""
                        <div class="value-card">
                            <div class="value-icon">{icon}</div>
                            <h3 class="value-title">{title}</h3>
                            <p class="value-description">{description}</p>
                        </div>
                    """, unsafe_allow_html=True)


def render_tool_cards():
    """Render 3 hero tool cards with navigation"""

    st.markdown('<h2 class="section-title">Choose Your Analysis Tool</h2>', unsafe_allow_html=True)

    tools = [
        {
            "icon": "🔍",
            "title": "Fund Deepdive",
            "description": "Comprehensive single-fund performance analysis with 30+ metrics, SIP progression tracking, benchmark comparison, and interactive visualizations. Perfect for deep research on specific funds.",
            "page": "fund_deepdive"
        },
        {
            "icon": "📈",
            "title": "Category Deepdive",
            "description": "Compare multiple funds within a category. View equity curves, correlation matrices, distribution charts, and performance rankings to identify category leaders.",
            "page": "category_deepdive"
        },
        {
            "icon": "🌐",
            "title": "Fund Universe",
            "description": "Portfolio-level analysis across categories. Explore fund metrics, distributions, and cross-category comparisons for diversified portfolio construction.",
            "page": "fund_universe"
        }
    ]

    cols = st.columns(3, gap="large")

    for idx, (col, tool) in enumerate(zip(cols, tools)):
        with col:
            st.markdown(f"""
                <div class="tool-card">
                    <div class="tool-icon">{tool['icon']}</div>
                    <h3 class="tool-title">{tool['title']}</h3>
                    <p class="tool-description">{tool['description']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Navigation button
            if st.button(f"Launch {tool['title']}", key=f"btn_{tool['page']}", use_container_width=True):
                st.switch_page(f"wip/pages/{tool['page']}.py")


def render_footer():
    """Render footer section"""
    st.markdown("""
        <div class="footer">
            <p>© 2024 Fund Investigator | Built with Streamlit | Powered by Cloudflare R2</p>
        </div>
    """, unsafe_allow_html=True)


def get_svg_b64(svg_path):
    """Load SVG file and convert to base64 for embedding"""
    import base64
    with open(svg_path, 'r') as f:
        svg_content = f.read()
    b64 = base64.b64encode(svg_content.encode()).decode()
    return b64


def render(data_loader=None):
    """Main render function for landing page

    Args:
        data_loader: Optional data loader (not used on landing page)
    """

    # Hide sidebar on landing page
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render sections
    render_hero_section()
    render_tool_cards()
    render_footer()
