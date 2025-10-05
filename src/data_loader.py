import pandas as pd
import duckdb
import streamlit as st
import os
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class R2DataLoader:
    """Data loader for Cloudflare R2 using DuckDB"""

    def __init__(self):
        self.conn = None
        self._setup_connection()

    def _setup_connection(self):
        """Setup DuckDB connection with R2 configuration"""
        try:
            with duckdb.connect() as conn:
                self.conn = duckdb.connect('./data/mf_data.db')

                # Install and load httpfs extension for S3/R2 support
                self.conn.execute("INSTALL httpfs;")
                self.conn.execute("LOAD httpfs;")

                # Configure R2 connection
                r2_config = {
                    'key_id': os.getenv('R2_ACCESS_KEY_ID'),
                    'secret': os.getenv('R2_SECRET_ACCESS_KEY'),
                    'endpoint': os.getenv('R2_ENDPOINT_URL'),
                    'region': os.getenv('R2_REGION', 'auto'),
                    'account_id': os.getenv('R2_ACCOUNT_ID')
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
            bucket = os.getenv('R2_BUCKET_NAME')
            data_path = os.getenv('R2_NAV_DATA_PATH')
            test_query = f"SELECT COUNT(*) FROM 's3://{bucket}/{data_path}' LIMIT 1;"
            self.conn.execute(test_query)
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def create_db_tables(self):
        """Create local DuckDB table from R2 data"""
        if not self.conn:
            print("No connection established")
        try:
            bucket = os.getenv('R2_BUCKET_NAME')
            data_path = os.getenv('R2_NAV_DATA_PATH')
            metadata_path = os.getenv('R2_MF_METADATA_PATH')
            benchmark_path = os.getenv('R2_MF_BENCHMARK_DATA_PATH')
            self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS mf_nav_daily_long AS
                SELECT * FROM read_parquet('s3://{bucket}/{data_path}')
            """)
            
            print("Table mf_nav_daily_long created successfully.")
            
            self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS mf_scheme_metadata AS
                SELECT * FROM read_parquet('s3://{bucket}/{metadata_path}')
            """)
            print("Table mf_scheme_metadata created successfully.")
            
            self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS mf_benchmark_daily_long AS
                SELECT * FROM read_parquet('s3://{bucket}/{benchmark_path}')
            """)
            print("Table mf_benchmark_daily_long created successfully.")

        except Exception as e:
            print(f"Failed to create tables: {str(e)}")

    @st.cache_data
    def get_available_funds(_self):
        """Get list of available funds (scheme names) from the dataset"""

        if not _self.conn:
            return None

        try:
            # Get unique fund schemes with category information, prioritizing popular/recent ones
            query = f"""
                SELECT * FROM mf_scheme_metadata
            """

            result = _self.conn.execute(query).df()
            result['display_name'] = result['scheme_name'] + ' |' + result['scheme_code'].astype(str)
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
            # Build the query to get the long format data
            scheme_codes = tuple(code.split('|')[1] for code in selected_fund_schemes)
            query = f"""
                SELECT * FROM mf_nav_daily_long
                WHERE date >= '{start_date}'
                  AND date <= '{end_date}'
                  AND scheme_code IN {scheme_codes}
            """
            df_long = _self.conn.execute(query).df()

            if df_long.empty:
                return None

            # Convert date to datetime
            df_long['date'] = pd.to_datetime(df_long['date'])
            df_long['display_name'] = df_long['scheme_name'] + ' |' + df_long['scheme_code'].astype(str)

            print('here')

            # Pivot from long to wide format - use scheme_name as columns
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

# Initialize global data loader
@st.cache_resource
def get_data_loader():
    """Get or create the R2 data loader instance"""
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