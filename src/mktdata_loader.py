"""Data loader using mktdata package - wrapper maintaining R2DataLoader interface"""
import pandas as pd
import streamlit as st
import os
import mktdata
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MktDataLoader:
    """Data loader wrapping mktdata package with R2DataLoader interface"""

    def __init__(self):
        """Initialize connection (mktdata handles configuration via ~/.mktdata/config.yaml)"""
        pass

    def test_connection(self):
        """Test mktdata connection"""
        try:
            # Try to query catalog metadata
            tables = mktdata.query("SELECT COUNT(*) FROM _catalog_meta")
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def create_db_tables(self):
        """No-op - mktdata manages catalog automatically"""
        # Mktdata handles catalog initialization, so this is a no-op
        # Just verify connection works
        try:
            cache_ttl_hours = int(os.getenv('CACHE_TTL_HOURS', '24'))
            print(f"Using mktdata catalog (cache TTL: {cache_ttl_hours} hours)...")

            # Verify tables exist
            catalog_df = mktdata.query("SELECT table_name FROM _catalog_meta ORDER BY table_name")
            tables = catalog_df['table_name'].tolist()
            print(f"Available tables: {', '.join(tables)}")

            # Get latest NAV date
            max_date_df = mktdata.query("SELECT MAX(date) as max_date FROM mf_nav_daily")
            max_date = max_date_df['max_date'].iloc[0]
            print(f"Data loaded successfully. Latest NAV date: {max_date}")
        except Exception as e:
            print(f"Warning: Could not verify mktdata tables: {str(e)}")

    @st.cache_data
    def get_available_funds(_self):
        """Get list of available funds with category information"""
        try:
            # Get schemes metadata, filtering for growth plans only
            query = """
                SELECT * FROM mf_schemes
                WHERE is_growth_plan = true
            """
            result = mktdata.query(query)

            # Add plan type (Direct/Regular) to display name
            result['plan_type'] = result['is_direct'].apply(lambda x: 'Direct' if x else 'Regular')
            result['display_name'] = result['scheme_name'] + ' - ' + result['plan_type'] + ' |' + result['scheme_code'].astype(str)
            return result
        except Exception as e:
            st.error(f"Failed to get available funds: {str(e)}")
            return None

    @st.cache_data
    def load_fund_data(_self, start_date=None, end_date=None, selected_fund_schemes=None):
        """Load fund data and pivot to wide format for analysis"""
        try:
            # Extract scheme codes from display names (format: "Name - Type |CODE")
            scheme_codes = tuple(code.split('|')[1] for code in selected_fund_schemes)

            # Build query with plan type from metadata
            query = f"""
                SELECT
                    nav.date,
                    nav.scheme_code,
                    nav.scheme_name,
                    nav.nav,
                    CASE WHEN meta.is_direct THEN 'Direct' ELSE 'Regular' END as plan_type
                FROM mf_nav_daily nav
                LEFT JOIN mf_schemes meta ON nav.scheme_code = meta.scheme_code
                WHERE nav.date >= '{start_date}'
                  AND nav.date <= '{end_date}'
                  AND nav.scheme_code IN {scheme_codes}
            """
            df_long = mktdata.query(query)

            if df_long.empty:
                return None

            # Convert date to datetime
            df_long['date'] = pd.to_datetime(df_long['date'])

            # Create display name with plan type to match selection format
            df_long['display_name'] = df_long['scheme_name'] + ' - ' + df_long['plan_type'] + ' |' + df_long['scheme_code'].astype(str)

            # Pivot from long to wide format - use display_name as columns
            df_wide = df_long.pivot(index='date', columns='display_name', values='nav')

            # Drop columns with all NaN values
            df_wide = df_wide.dropna(axis=1, how='all')

            # Sort by date
            df_wide = df_wide.sort_index()
            return df_wide

        except Exception as e:
            st.error(f"Failed to load fund data: {str(e)}")
            return None

    @st.cache_data
    def load_fund_data_long(_self, start_date=None, end_date=None, selected_fund_schemes=None):
        """Load fund data in long format"""
        try:
            # Extract scheme codes from display names
            scheme_codes = tuple(code.split('|')[1] for code in selected_fund_schemes)

            # Build query with category and plan type from metadata
            query = f"""
                SELECT
                    nav.date,
                    nav.scheme_code,
                    nav.scheme_name,
                    nav.nav,
                    meta.scheme_category_level1,
                    meta.scheme_category_level2,
                    CASE WHEN meta.is_direct THEN 'Direct' ELSE 'Regular' END as plan_type
                FROM mf_nav_daily nav
                LEFT JOIN mf_schemes meta ON nav.scheme_code = meta.scheme_code
                WHERE nav.date >= '{start_date}'
                  AND nav.date <= '{end_date}'
                  AND nav.scheme_code IN {scheme_codes}
            """
            df_long = mktdata.query(query)

            if df_long.empty:
                return None

            # Convert date to datetime
            df_long['date'] = pd.to_datetime(df_long['date'])

            # Create display name with plan type to match selection format
            df_long['display_name'] = df_long['scheme_name'] + ' - ' + df_long['plan_type'] + ' |' + df_long['scheme_code'].astype(str)

            return df_long

        except Exception as e:
            st.error(f"Failed to load fund data: {str(e)}")
            return None

    @st.cache_data
    def get_data_date_range(_self):
        """Get the min and max date available in the dataset"""
        try:
            query = "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM mf_nav_daily"
            result = mktdata.query(query)
            min_date = pd.to_datetime(result['min_date'].iloc[0]).date()
            max_date = pd.to_datetime(result['max_date'].iloc[0]).date()
            return min_date, max_date
        except Exception as e:
            st.error(f"Failed to get data date range: {str(e)}")
            return None, None

    @st.cache_data
    def get_fund_date_range(_self, scheme_code):
        """Get the min and max date for a specific fund"""
        try:
            query = f"""
                SELECT MIN(date) AS min_date, MAX(date) AS max_date
                FROM mf_nav_daily
                WHERE scheme_code = '{scheme_code}'
            """
            result = mktdata.query(query)
            min_date = pd.to_datetime(result['min_date'].iloc[0]).date()
            max_date = pd.to_datetime(result['max_date'].iloc[0]).date()
            return min_date, max_date
        except Exception as e:
            st.error(f"Failed to get fund date range: {str(e)}")
            return None, None

    @st.cache_data
    def get_benchmark_date_range(_self, index_name, index_type):
        """Get the min and max date for a specific benchmark"""
        try:
            query = f"""
                SELECT MIN(date) AS min_date, MAX(date) AS max_date
                FROM mf_benhcmark_daily
                WHERE index_name = '{index_name}' AND index_type = '{index_type}'
            """
            result = mktdata.query(query)
            min_date = pd.to_datetime(result['min_date'].iloc[0]).date()
            max_date = pd.to_datetime(result['max_date'].iloc[0]).date()
            return min_date, max_date
        except Exception as e:
            st.error(f"Failed to get benchmark date range: {str(e)}")
            return None, None

    @st.cache_data
    def get_benchmark_options(_self, index_type=None, index_category=None):
        """Get available benchmark indices based on filters"""
        try:
            query = "SELECT DISTINCT index_name FROM mf_benhcmark_daily WHERE 1=1"

            if index_type:
                query += f" AND index_type = '{index_type}'"

            if index_category and index_category != 'ALL':
                query += f" AND index_category = '{index_category}'"

            query += " ORDER BY index_name"

            result = mktdata.query(query)
            return result['index_name'].tolist()
        except Exception as e:
            st.error(f"Failed to get benchmark options: {str(e)}")
            return []

    @st.cache_data
    def load_benchmark_data(_self, index_name, index_type, start_date=None, end_date=None):
        """Load benchmark data"""
        try:
            query = f"""
                SELECT date, close as value
                FROM mf_benhcmark_daily
                WHERE index_name = '{index_name}'
                  AND index_type = '{index_type}'
            """

            if start_date:
                query += f" AND date >= '{start_date}'"
            if end_date:
                query += f" AND date <= '{end_date}'"

            query += " ORDER BY date"

            df = mktdata.query(query)

            if df.empty:
                return None

            # Convert to series with date index
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            return df['value']

        except Exception as e:
            st.error(f"Failed to load benchmark data: {str(e)}")
            return None

    def load_fund_data_all(_self):
        """Load all fund data in long format"""
        try:
            query = """
                SELECT
                    nav.date,
                    nav.scheme_code,
                    nav.scheme_name,
                    nav.nav,
                    meta.scheme_category_level1,
                    meta.scheme_category_level2,
                    CASE WHEN meta.is_direct THEN 'Direct' ELSE 'Regular' END as plan_type
                FROM mf_nav_daily nav
                LEFT JOIN mf_schemes meta ON nav.scheme_code = meta.scheme_code
            """
            df_long = mktdata.query(query)

            # Convert date to datetime
            df_long['date'] = pd.to_datetime(df_long['date'])
            return df_long

        except Exception as e:
            st.error(f"Failed to load fund data: {str(e)}")
            return None


# Initialize global data loader
@st.cache_resource
def get_data_loader():
    """Get or create the MktData loader instance with caching

    Uses Streamlit's cache_resource to ensure a single data loader instance
    is shared across all sessions and cached in memory.
    """
    return MktDataLoader()


# Legacy function compatibility
def get_fund_columns(df):
    """Extract fund column names from dataframe (legacy compatibility)"""
    if df is None:
        return []
    return [col for col in df.columns if col.lower() not in ['date', 'index', 'id']]


def filter_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range (legacy compatibility)"""
    if df is None:
        return None
    return df.loc[start_date:end_date]


def calculate_returns(nav_series):
    """Calculate daily returns from NAV series"""
    if nav_series is None or nav_series.empty:
        return pd.Series(dtype=float)
    return nav_series.pct_change().dropna()
