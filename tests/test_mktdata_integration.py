"""Test mktdata package connectivity and data structure"""
import mktdata
import pandas as pd

def test_mktdata_tables():
    """Verify all required tables are available"""
    # Print table info (for debugging)
    print("\n" + "="*60)
    mktdata.tables()
    print("="*60)

    # Query catalog metadata to verify tables
    catalog_df = mktdata.query("SELECT table_name FROM _catalog_meta ORDER BY table_name")
    available_tables = catalog_df['table_name'].tolist()
    print("\nAvailable table names:", available_tables)

    required_tables = ['mf_nav_daily', 'mf_schemes', 'mf_benhcmark_daily']
    for table in required_tables:
        assert table in available_tables, f"Missing table: {table}"

def test_nav_data_structure():
    """Verify NAV data has expected columns"""
    nav_df = mktdata.query("SELECT * FROM mf_nav_daily LIMIT 10")
    print("\nNAV columns:", nav_df.columns.tolist())

    # Expected: date, scheme_code, scheme_name, nav
    expected_cols = ['date', 'scheme_code', 'scheme_name', 'nav']
    for col in expected_cols:
        assert col in nav_df.columns, f"Missing column: {col}"

def test_schemes_data_structure():
    """Verify schemes metadata has expected columns"""
    schemes_df = mktdata.query("SELECT * FROM mf_schemes LIMIT 10")
    print("\nSchemes columns:", schemes_df.columns.tolist())

    # Expected: scheme_code, scheme_name, scheme_category_level1, scheme_category_level2
    expected_cols = ['scheme_code', 'scheme_name', 'scheme_category_level1', 'scheme_category_level2']
    for col in expected_cols:
        assert col in schemes_df.columns, f"Missing column: {col}"

def test_benchmark_data_structure():
    """Verify benchmark data has expected columns"""
    bench_df = mktdata.query("SELECT * FROM mf_benhcmark_daily LIMIT 10")
    print("\nBenchmark columns:", bench_df.columns.tolist())

    # Benchmark data has different structure: uses index_name, close, etc.
    expected_cols = ['date', 'index_name', 'close', 'index_type', 'index_category']
    for col in expected_cols:
        assert col in bench_df.columns, f"Missing column: {col}"

def test_date_range_query():
    """Test date range queries work as expected"""
    result = mktdata.query("""
        SELECT MIN(date) as min_date, MAX(date) as max_date
        FROM mf_nav_daily
    """)
    print("\nDate range:", result)
    assert result is not None

if __name__ == "__main__":
    test_mktdata_tables()
    test_nav_data_structure()
    test_schemes_data_structure()
    test_benchmark_data_structure()
    test_date_range_query()
    print("\n✅ All mktdata tests passed!")
