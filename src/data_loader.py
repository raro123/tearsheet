import pandas as pd
import duckdb
import streamlit as st
import os
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables (only if .env exists - for local development)
if os.path.exists('.env'):
    load_dotenv()

def get_env_or_secret(key: str, secret_path: list = None):
    """Get value from environment variable or Streamlit secrets

    Args:
        key: Environment variable name
        secret_path: Path in st.secrets (e.g., ['r2', 'access_key_id'])

    Returns:
        Value from environment variable or Streamlit secrets, or None if not found
    """
    # Try environment variable first (local dev)
    value = os.getenv(key)
    if value:
        return value

    # Try Streamlit secrets (cloud deployment)
    try:
        if secret_path:
            obj = st.secrets
            for part in secret_path:
                obj = obj[part]
            return obj
        return st.secrets.get(key)
    except (KeyError, AttributeError, FileNotFoundError):
        return None

class R2DataLoader:
    """Data loader for Cloudflare R2 using DuckDB"""

    def __init__(self):
        self.conn = None
        self._setup_connection()

    def _setup_connection(self):
        """Setup DuckDB in-memory connection with R2 configuration"""
        try:
            # Use in-memory database instead of persistent file
            self.conn = duckdb.connect(':memory:')

            # Install and load httpfs extension for S3/R2 support
            self.conn.execute("INSTALL httpfs;")
            self.conn.execute("LOAD httpfs;")

            # Configure R2 connection
            r2_config = {
                'key_id': get_env_or_secret('R2_ACCESS_KEY_ID', ['r2', 'access_key_id']),
                'secret': get_env_or_secret('R2_SECRET_ACCESS_KEY', ['r2', 'secret_access_key']),
                'endpoint': get_env_or_secret('R2_ENDPOINT_URL', ['r2', 'endpoint_url']),
                'region': get_env_or_secret('R2_REGION', ['r2', 'region']) or 'auto',
                'account_id': get_env_or_secret('R2_ACCOUNT_ID', ['r2', 'account_id'])
            }

            # Clean endpoint URL - remove protocol if present
            if r2_config['endpoint']:
                endpoint = r2_config['endpoint'].replace('https://', '').replace('http://', '')
                r2_config['endpoint'] = endpoint

            # Set S3 configuration for R2 using DuckDB SECRET
            self.conn.execute(f"""
                CREATE OR REPLACE SECRET r2_secret (
                    TYPE S3,
                    KEY_ID '{r2_config['key_id']}',
                    SECRET '{r2_config['secret']}',
                    ENDPOINT '{r2_config['endpoint']}',
                    URL_STYLE 'path',
                    USE_SSL true
                )
            """)

        except Exception as e:
                st.error(f"Failed to setup R2 connection: {str(e)}")
                self.conn = None

    def test_connection(self):
        """Test R2 connection"""
        if not self.conn:
            return False, "No connection established"

        try:
            bucket = get_env_or_secret('R2_BUCKET_NAME', ['r2', 'bucket_name'])
            data_path = get_env_or_secret('R2_NAV_DATA_PATH', ['data', 'nav_data_path'])
            test_query = f"SELECT COUNT(*) FROM 's3://{bucket}/{data_path}' LIMIT 1;"
            self.conn.execute(test_query)
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    @st.cache_resource(ttl=86400)  # Cache for 24 hours (configurable via CACHE_TTL_HOURS env var)
    def create_db_tables(_self):
        """Create in-memory DuckDB tables from R2 data with TTL-based caching

        This method is cached by Streamlit with a 24-hour TTL (Time To Live).
        After 24 hours, the cache expires and data is automatically refreshed from R2.
        """
        if not _self.conn:
            print("No connection established")
            return

        try:
            # Get cache TTL from environment (in hours), default 24 hours
            cache_ttl_hours = int(get_env_or_secret('CACHE_TTL_HOURS', ['cache', 'ttl_hours']) or '24')

            bucket = get_env_or_secret('R2_BUCKET_NAME', ['r2', 'bucket_name'])
            data_path = get_env_or_secret('R2_NAV_DATA_PATH', ['data', 'nav_data_path'])
            metadata_path = get_env_or_secret('R2_MF_METADATA_PATH', ['data', 'metadata_path'])
            benchmark_path = get_env_or_secret('R2_MF_BENCHMARK_DATA_PATH', ['data', 'benchmark_data_path'])

            print(f"Loading data from R2 (cache TTL: {cache_ttl_hours} hours)...")

            # Create tables from R2 parquet files
            _self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS mf_nav_daily_long AS
                SELECT * FROM read_parquet('s3://{bucket}/{data_path}')
            """)
            print("Table mf_nav_daily_long created successfully.")

            _self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS mf_scheme_metadata AS
                SELECT * FROM read_parquet('s3://{bucket}/{metadata_path}')
            """)
            print("Table mf_scheme_metadata created successfully.")

            _self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS mf_benchmark_daily_long AS
                SELECT * FROM read_parquet('s3://{bucket}/{benchmark_path}')
            """)
            print("Table mf_benchmark_daily_long created successfully.")

            # Log data freshness
            max_date = _self.conn.execute("""
                SELECT MAX(date) FROM mf_nav_daily_long
            """).fetchone()[0]
            print(f"Data loaded successfully. Latest NAV date: {max_date}")

        except Exception as e:
            print(f"Failed to create tables: {str(e)}")

    @st.cache_data
    def get_available_funds(_self):
        """Get list of available funds (scheme names) from the dataset"""

        if not _self.conn:
            return None

        try:
            # Get unique fund schemes with category information, filtering for growth plans only
            query = f"""
                SELECT * FROM mf_scheme_metadata
                WHERE is_growth_plan = true
            """

            result = _self.conn.execute(query).df()
            # Add plan type (Direct/Regular) to display name
            result['plan_type'] = result['is_direct'].apply(lambda x: 'Direct' if x else 'Regular')
            result['display_name'] = result['scheme_name'] + ' - ' + result['plan_type'] + ' |' + result['scheme_code'].astype(str)
            return result
        except Exception as e:
            st.error(f"Failed to get available funds: {str(e)}")
            return None

    @st.cache_data
    def load_fund_data(_self, start_date=None, end_date=None, selected_fund_schemes=None):
        """Load fund data from R2 and pivot to wide format for analysis"""

        if not _self.conn:
            return None

        try:
            # Build the query to get the long format data with plan type from metadata
            scheme_codes = tuple(code.split('|')[1] for code in selected_fund_schemes)
            query = f"""
                SELECT
                    nav.date,
                    nav.scheme_code,
                    nav.scheme_name,
                    nav.nav,
                    CASE WHEN meta.is_direct THEN 'Direct' ELSE 'Regular' END as plan_type
                FROM mf_nav_daily_long nav
                LEFT JOIN mf_scheme_metadata meta ON nav.scheme_code = meta.scheme_code
                WHERE nav.date >= '{start_date}'
                  AND nav.date <= '{end_date}'
                  AND nav.scheme_code IN {scheme_codes}
            """
            df_long = _self.conn.execute(query).df()

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
        """Load fund data from R2 and pivot to wide format for analysis"""

        if not _self.conn:
            return None

        try:
            # Build the query to get the long format data with plan type from metadata
            scheme_codes = tuple(code.split('|')[1] for code in selected_fund_schemes)
            query = f"""
                SELECT
                    nav.date,
                    nav.scheme_code,
                    nav.scheme_name,
                    nav.nav,
                    meta.scheme_category_level1,
                    meta.scheme_category_level2,
                    CASE WHEN meta.is_direct THEN 'Direct' ELSE 'Regular' END as plan_type
                FROM mf_nav_daily_long nav
                LEFT JOIN mf_scheme_metadata meta ON nav.scheme_code = meta.scheme_code
                WHERE nav.date >= '{start_date}'
                  AND nav.date <= '{end_date}'
                  AND nav.scheme_code IN {scheme_codes}
            """
            df_long = _self.conn.execute(query).df()

            if df_long.empty:
                return None

            # Convert date to datetime
            df_long['date'] = pd.to_datetime(df_long['date'])
            # Create display name with plan type to match selection format
            df_long['display_name'] = df_long['scheme_name'] + ' - ' + df_long['plan_type'] + ' |' + df_long['scheme_code'].astype(str)

        except Exception as e:
            st.error(f"Failed to load fund data: {str(e)}")
            return None
        
        return df_long
    
    @st.cache_data
    def get_data_date_range(_self):
        """Get the min and max date available in the dataset"""
        if not _self.conn:
            return None, None
        try:
            query = "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM mf_nav_daily_long"
            result = _self.conn.execute(query).df()
            min_date = pd.to_datetime(result['min_date'].iloc[0]).date()
            max_date = pd.to_datetime(result['max_date'].iloc[0]).date()
            return min_date, max_date
        except Exception as e:
            st.error(f"Failed to get data date range: {str(e)}")
            return None, None

    @st.cache_data
    def get_fund_date_range(_self, scheme_code):
        """Get the min and max date for a specific fund"""
        if not _self.conn:
            return None, None
        try:
            query = f"""
                SELECT MIN(date) AS min_date, MAX(date) AS max_date
                FROM mf_nav_daily_long
                WHERE scheme_code = '{scheme_code}'
            """
            result = _self.conn.execute(query).df()
            min_date = pd.to_datetime(result['min_date'].iloc[0]).date()
            max_date = pd.to_datetime(result['max_date'].iloc[0]).date()
            return min_date, max_date
        except Exception as e:
            st.error(f"Failed to get fund date range: {str(e)}")
            return None, None

    @st.cache_data
    def get_benchmark_date_range(_self, index_name, index_type):
        """Get the min and max date for a specific benchmark"""
        if not _self.conn:
            return None, None
        try:
            query = f"""
                SELECT MIN(date) AS min_date, MAX(date) AS max_date
                FROM mf_benchmark_daily_long
                WHERE index_name = '{index_name}' AND index_type = '{index_type}'
            """
            result = _self.conn.execute(query).df()
            min_date = pd.to_datetime(result['min_date'].iloc[0]).date()
            max_date = pd.to_datetime(result['max_date'].iloc[0]).date()
            return min_date, max_date
        except Exception as e:
            st.error(f"Failed to get benchmark date range: {str(e)}")
            return None, None

    @st.cache_data
    def get_benchmark_options(_self, index_type=None, index_category=None):
        """Get available benchmark indices based on filters"""
        if not _self.conn:
            return []

        try:
            query = "SELECT DISTINCT index_name FROM mf_benchmark_daily_long WHERE 1=1"

            if index_type:
                query += f" AND index_type = '{index_type}'"

            if index_category and index_category != 'ALL':
                query += f" AND index_category = '{index_category}'"

            query += " ORDER BY index_name"

            result = _self.conn.execute(query).df()
            return result['index_name'].tolist()
        except Exception as e:
            st.error(f"Failed to get benchmark options: {str(e)}")
            return []

    @st.cache_data
    def load_benchmark_data(_self, index_name, index_type, start_date=None, end_date=None):
        """Load benchmark data from R2"""
        if not _self.conn:
            return None

        try:
            query = f"""
                SELECT date, close as value
                FROM mf_benchmark_daily_long
                WHERE index_name = '{index_name}'
                  AND index_type = '{index_type}'
            """

            if start_date:
                query += f" AND date >= '{start_date}'"
            if end_date:
                query += f" AND date <= '{end_date}'"

            query += " ORDER BY date"

            df = _self.conn.execute(query).df()

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
        """Load fund data from R2 and pivot to wide format for analysis"""
        print("0")
        if not _self.conn:
            print("1")
            return None

        try:
            print("2")
            query = f"""
                SELECT
                    nav.date,
                    nav.scheme_code,
                    nav.scheme_name,
                    nav.nav,
                    meta.scheme_category_level1,
                    meta.scheme_category_level2,
                    CASE WHEN meta.is_direct THEN 'Direct' ELSE 'Regular' END as plan_type
                FROM mf_nav_daily_long nav
                LEFT JOIN mf_scheme_metadata meta ON nav.scheme_code = meta.scheme_code
            """
            df_long = _self.conn.execute(query).df()
            print("executed")
            # Convert date to datetime
            df_long['date'] = pd.to_datetime(df_long['date'])
            return df_long

        except Exception as e:
            print(e)
            st.error(f"Failed to load fund data: {str(e)}")
            return None
        


# Initialize global data loader
@st.cache_resource
def get_data_loader():
    """Get or create the R2 data loader instance with caching

    Uses Streamlit's cache_resource to ensure a single data loader instance
    is shared across all sessions and cached in memory.
    """
    return R2DataLoader()

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