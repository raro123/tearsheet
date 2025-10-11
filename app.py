"""
Mutual Fund Performance Analysis - Multipage App

A comprehensive Streamlit application for analyzing mutual fund performance
with multiple analysis views and interactive visualizations.
"""
import streamlit as st
from src.data_loader import get_data_loader

# Import page modules
import pages.fund_universe as page_fund_universe
import pages.category_deepdive as page_category_deepdive
import pages.fund_deepdive as page_fund_deepdive

# Page configuration
st.set_page_config(
    page_title="Mutual Fund Analysis Platform",
    page_icon="📊",
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
def category_deepdive_page():
    """Wrapper for category deepdive page"""
    page_category_deepdive.render(st.session_state.data_loader)

def fund_deepdive_page():
    """Wrapper for fund deepdive page"""
    page_fund_deepdive.render(st.session_state.data_loader)

# Navigation setup
pg = st.navigation([
    st.Page(page_fund_universe.render, title="Fund Universe", icon="🌐", default=False),
    st.Page(category_deepdive_page, title="Category Deepdive", icon="📈", default=True),
    st.Page(fund_deepdive_page, title="Fund Deepdive", icon="🔍")
])

# Run the selected page
pg.run()
