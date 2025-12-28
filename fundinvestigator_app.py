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

    /* Hide default Streamlit header padding */
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Store logo function in session state for use in pages
def get_logo_base64():
    """Load logo and convert to base64"""
    logo_path = Path(__file__).parent / \
        "fundinvestigator-brand-package/brand-package-final/logo-primary.svg"
    with open(logo_path, 'r') as f:
        svg_content = f.read()
    return base64.b64encode(svg_content.encode()).decode()

# Store logo base64 in session state for reuse
if 'logo_base64' not in st.session_state:
    st.session_state.logo_base64 = get_logo_base64()

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
