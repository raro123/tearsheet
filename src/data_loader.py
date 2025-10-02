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
            self.conn = duckdb.connect()

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

    @st.cache_data
    def get_data_info(_self):
        """Get basic information about the dataset"""
        bucket = os.getenv('R2_BUCKET_NAME')
        data_path = os.getenv('R2_NAV_DATA_PATH')

        if not _self.conn:
            return None

        try:
            # Get basic stats about the dataset
            query = f"""
            SELECT
                COUNT(*) as total_rows,
                MIN(date) as min_date,
                MAX(date) as max_date,
                COUNT(DISTINCT date) as unique_dates
            FROM 's3://{bucket}/{data_path}'
            WHERE date IS NOT NULL;
            """

            result = _self.conn.execute(query).fetchone()
            return {
                'total_rows': result[0],
                'min_date': result[1],
                'max_date': result[2],
                'unique_dates': result[3],
                'file_path': f"{bucket}/{data_path}"
            }
        except Exception as e:
            st.error(f"Failed to get data info: {str(e)}")
            return None

    @st.cache_data
    def get_available_funds(_self, limit=1000):
        """Get list of available funds (scheme names) from the dataset"""
        bucket = os.getenv('R2_BUCKET_NAME')
        data_path = os.getenv('R2_NAV_DATA_PATH')

        if not _self.conn:
            return []

        try:
            # Get unique fund schemes with category information, prioritizing popular/recent ones
            query = f"""
            WITH fund_stats AS (
                SELECT
                    scheme_name,
                    scheme_code,
                    amc_name,
                    scheme_name || ' |' || scheme_code as display_name,
                    FIRST(scheme_category_level1) as scheme_category_level1,
                    FIRST(scheme_category_level2) as scheme_category_level2,
                    COUNT(*) as data_points,
                    MAX(date) as latest_date
                FROM 's3://{bucket}/{data_path}'
                WHERE scheme_name IS NOT NULL
                AND nav IS NOT NULL
                GROUP BY scheme_name, scheme_code, amc_name, display_name
                ORDER BY data_points DESC, latest_date DESC
                LIMIT {limit}
            )
            SELECT * FROM fund_stats;
            """

            result = _self.conn.execute(query).df()

            # Create a list of fund options with descriptive names
            # funds = []
            # for row in result:
            #     scheme_name, scheme_code, amc_name, cat_level1, cat_level2, data_points, latest_date = row
            #     fund_display = f"{scheme_name} ({scheme_code})"
            #     funds.append({
            #         'display_name': fund_display,
            #         'scheme_name': scheme_name,
            #         'scheme_code': scheme_code,
            #         'amc_name': amc_name,
            #         'category_level1': cat_level1 if cat_level1 else "Uncategorized",
            #         'category_level2': cat_level2 if cat_level2 else "Uncategorized",
            #         'data_points': data_points,
            #         'latest_date': latest_date
            #     })

            return result
        except Exception as e:
            st.error(f"Failed to get available funds: {str(e)}")
            return None

    @st.cache_data
    def load_fund_data(_self, start_date=None, end_date=None, selected_fund_schemes=None):
        """Load fund data from R2 and pivot to wide format for analysis"""
        bucket = os.getenv('R2_BUCKET_NAME')
        data_path = os.getenv('R2_NAV_DATA_PATH')

        if not _self.conn:
            return None

        try:
            # Build the query to get the long format data
            df_long = (_self.conn.read_parquet(f"s3://{bucket}/{data_path}")
             .filter(f"date>='{start_date}'")
             .filter(f"date<='{end_date}'")
             .filter(f"scheme_code IN {tuple(code.split('|')[1] for code in  selected_fund_schemes)}")
            .df()
             )
            # where_conditions = ["nav IS NOT NULL", "date IS NOT NULL"]

            # # Add fund filtering if provided
            # # if selected_fund_schemes:
            # #     fund_filter = "', '".join([scheme for scheme in selected_fund_schemes])
            # #     where_conditions.append(f"display_name IN ('{fund_filter}')")

            # # Add date filtering if provided
            # if start_date:
            #     where_conditions.append(f"date >= '{start_date}'")
            # if end_date:
            #     where_conditions.append(f"date <= '{end_date}'")

            # query = f"""
            # SELECT
            #     date,
            #     scheme_name,
            #     amc_name,
            #     scheme_code,
            #     display_name,
            #     nav
            # FROM 's3://{bucket}/{data_path}'
            # WHERE {' OR '.join(where_conditions)}
            # ORDER BY date, scheme_name;
            # """

            # Execute query and get DataFrame

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

def get_available_funds_list(data_loader):
    """Get list of available funds for UI selection"""
    return data_loader.get_available_funds()

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