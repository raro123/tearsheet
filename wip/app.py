"""
Mutual Fund Performance Analysis - Multipage App

A comprehensive Streamlit application for analyzing mutual fund performance
with multiple analysis views and interactive visualizations.
"""
import streamlit as st
from src.data_loader import get_data_loader

# Import page modules
import wip.pages.landing as page_landing
import wip.pages.fund_universe as page_fund_universe
import wip.pages.category_deepdive as page_category_deepdive
import app_pages.fund_deepdive as page_fund_deepdive

# Page configuration
st.set_page_config(
    page_title="Mutual Fund Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Navy/Gold Brand Theme
st.markdown("""
    <style>
    :root {
        --navy-primary: #1E3A5F;
        --gold-accent: #D4AF37;
        --gray-secondary: #64748B;
        --gray-light: #94A3B8;
    }

    /* ============================================
       LANDING PAGE - Hero Section
       ============================================ */
    .hero-section {
        background: linear-gradient(135deg, #1E3A5F 0%, #2D5A8F 100%);
        padding: 4rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 4px 20px rgba(30, 58, 95, 0.15);
    }

    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }

    .hero-logo {
        width: 400px;
        max-width: 90%;
        height: auto;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.1));
    }

    .hero-headline {
        font-size: 3rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }

    .hero-subheadline {
        font-size: 1.5rem;
        font-weight: 400;
        color: #D4AF37;
        margin-bottom: 0;
        letter-spacing: 0.5px;
    }

    /* ============================================
       LANDING PAGE - Section Titles
       ============================================ */
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        text-align: center;
        margin: 3rem 0 2rem 0;
        letter-spacing: -0.5px;
    }

    /* ============================================
       LANDING PAGE - Value Proposition Cards
       ============================================ */
    .value-card {
        background: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 200px;
    }

    .value-card:hover {
        border-color: #D4AF37;
        box-shadow: 0 8px 24px rgba(212, 175, 55, 0.15);
        transform: translateY(-4px);
    }

    .value-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .value-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.75rem;
    }

    .value-description {
        font-size: 0.95rem;
        color: #64748B;
        line-height: 1.6;
        margin-bottom: 0;
    }

    /* ============================================
       LANDING PAGE - Tool Hero Cards
       ============================================ */
    .tool-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F9FAFB 100%);
        border: 3px solid #1E3A5F;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    .tool-card:hover {
        border-color: #D4AF37;
        box-shadow: 0 12px 32px rgba(30, 58, 95, 0.2);
        transform: translateY(-6px);
    }

    .tool-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }

    .tool-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 1rem;
        letter-spacing: -0.3px;
    }

    .tool-description {
        font-size: 1rem;
        color: #64748B;
        line-height: 1.7;
        margin-bottom: 1.5rem;
        flex-grow: 1;
    }

    /* ============================================
       LANDING PAGE - Launch Buttons
       ============================================ */
    .stButton > button {
        background: linear-gradient(135deg, #1E3A5F 0%, #2D5A8F 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: auto;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #C99F2D 100%);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.3);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* ============================================
       LANDING PAGE - Footer
       ============================================ */
    .footer {
        background: #F9FAFB;
        padding: 2rem;
        text-align: center;
        margin-top: 4rem;
        border-top: 1px solid #E5E7EB;
        border-radius: 0 0 12px 12px;
    }

    .footer p {
        color: #94A3B8;
        font-size: 0.9rem;
        margin: 0;
    }

    /* ============================================
       EXISTING PAGES - Headers
       ============================================ */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }

    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {
        .hero-headline {
            font-size: 2rem;
        }
        .hero-subheadline {
            font-size: 1.2rem;
        }
        .section-title {
            font-size: 2rem;
        }
        .tool-card {
            min-height: 300px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize data loader in session state (shared across pages)
if 'data_loader' not in st.session_state:
    try:
        data_loader = get_data_loader()
        data_loader.create_db_tables()
        st.session_state.data_loader = data_loader
    except Exception as e:
        st.error(f"❌ Failed to initialize data loader: {str(e)}")
        st.stop()

# Create wrapper functions with unique names for navigation
def landing_page():
    """Wrapper for landing page"""
    page_landing.render()

def category_deepdive_page():
    """Wrapper for category deepdive page"""
    page_category_deepdive.render(st.session_state.data_loader)

def fund_deepdive_page():
    """Wrapper for fund deepdive page"""
    page_fund_deepdive.render(st.session_state.data_loader)

def fund_universe_page():
    """Wrapper for fund universe page"""
    page_fund_universe.render(st.session_state.data_loader)

# Navigation setup
pg = st.navigation([
    st.Page(landing_page, title="Home", icon="🏠", default=True),
    st.Page(fund_deepdive_page, title="Fund Deepdive", icon="🔍", default=False),
    st.Page(category_deepdive_page, title="Category Deepdive", icon="📈", default=False),
    st.Page(fund_universe_page, title="Fund Universe", icon="🌐", default=False)
])

# Run the selected page
pg.run()
