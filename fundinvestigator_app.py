"""
Fund Investigator - Standalone Application

A focused Streamlit application for comprehensive single-fund performance analysis
with interactive visualizations, metrics comparison, and SIP calculations.
"""
import streamlit as st
import base64
from pathlib import Path
from src.data_loader import get_data_loader
import app_pages.fund_deepdive as page_fund_deepdive

# Page configuration
st.set_page_config(
    page_title="Fund Investigator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }

    /* Logo header */
    .logo-header {
        position: fixed;
        top: 20px;
        right: 30px;
        z-index: 999;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }

    /* Ensure main content doesn't overlap with logo */
    .main .block-container {
        padding-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Add logo to top right header
def get_logo_base64():
    """Load logo and convert to base64"""
    logo_path = Path(__file__).parent / \
        "fundinvestigator-brand-package/brand-package-final/logo-primary.svg"
    with open(logo_path, 'r') as f:
        svg_content = f.read()
    return base64.b64encode(svg_content.encode()).decode()

# Render logo in top right
st.markdown(f"""
    <div style="position: fixed; top: 20px; right: 30px; z-index: 999;">
        <img src="data:image/svg+xml;base64,{get_logo_base64()}"
             alt="Fund Investigator"
             style="width: 140px; height: auto; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">
    </div>
""", unsafe_allow_html=True)

# Initialize data loader in session state
if 'data_loader' not in st.session_state:
    try:
        data_loader = get_data_loader()
        data_loader.create_db_tables()
        st.session_state.data_loader = data_loader
    except Exception as e:
        st.error(f"❌ Failed to initialize data loader: {str(e)}")
        st.stop()

# Render Fund Deepdive page
page_fund_deepdive.render(st.session_state.data_loader)
