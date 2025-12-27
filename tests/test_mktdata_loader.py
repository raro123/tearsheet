"""Unit tests for MktDataLoader wrapper class"""
import pandas as pd
from src.data_loader import get_data_loader, MktDataLoader


def test_get_data_loader():
    """Test that get_data_loader returns MktDataLoader instance"""
    loader = get_data_loader()
    assert loader is not None
    assert isinstance(loader, MktDataLoader)
    print("✅ get_data_loader() returns MktDataLoader instance")


def test_connection():
    """Test connection to mktdata catalog"""
    loader = get_data_loader()
    success, message = loader.test_connection()
    assert success, f"Connection failed: {message}"
    print(f"✅ Connection test passed: {message}")


def test_get_available_funds():
    """Test getting available funds"""
    loader = get_data_loader()
    funds = loader.get_available_funds()

    assert funds is not None, "get_available_funds returned None"
    assert isinstance(funds, pd.DataFrame), "get_available_funds should return DataFrame"
    assert len(funds) > 0, "No funds returned"
    assert 'display_name' in funds.columns, "Missing display_name column"
    assert 'scheme_code' in funds.columns, "Missing scheme_code column"
    assert 'scheme_category_level1' in funds.columns, "Missing scheme_category_level1 column"

    print(f"✅ Found {len(funds)} available funds")
    print(f"   Sample fund: {funds['display_name'].iloc[0]}")


def test_load_fund_data_wide():
    """Test loading fund data in wide format"""
    loader = get_data_loader()

    # Use a known scheme code (get first available fund)
    funds = loader.get_available_funds()
    test_fund = funds['display_name'].iloc[0]

    df = loader.load_fund_data(
        start_date='2024-01-01',
        end_date='2024-12-31',
        selected_fund_schemes=[test_fund]
    )

    assert df is not None, "load_fund_data returned None"
    assert isinstance(df, pd.DataFrame), "load_fund_data should return DataFrame"
    assert len(df) > 0, "No data returned"
    assert df.index.name == 'date' or isinstance(df.index, pd.DatetimeIndex), "Index should be date"

    print(f"✅ Loaded wide-format fund data")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    print(f"   Shape: {df.shape}")


def test_load_fund_data_long():
    """Test loading fund data in long format"""
    loader = get_data_loader()

    # Use a known scheme code
    funds = loader.get_available_funds()
    test_fund = funds['display_name'].iloc[0]

    df = loader.load_fund_data_long(
        start_date='2024-01-01',
        end_date='2024-12-31',
        selected_fund_schemes=[test_fund]
    )

    assert df is not None, "load_fund_data_long returned None"
    assert isinstance(df, pd.DataFrame), "load_fund_data_long should return DataFrame"
    assert len(df) > 0, "No data returned"
    assert 'date' in df.columns, "Missing date column"
    assert 'scheme_code' in df.columns, "Missing scheme_code column"
    assert 'nav' in df.columns, "Missing nav column"
    assert 'scheme_category_level1' in df.columns, "Missing scheme_category_level1"

    print(f"✅ Loaded long-format fund data")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {df.columns.tolist()}")


def test_get_data_date_range():
    """Test getting overall date range"""
    loader = get_data_loader()
    min_date, max_date = loader.get_data_date_range()

    assert min_date is not None, "min_date is None"
    assert max_date is not None, "max_date is None"
    assert min_date < max_date, "min_date should be less than max_date"

    print(f"✅ Overall date range: {min_date} to {max_date}")


def test_get_fund_date_range():
    """Test getting date range for specific fund"""
    loader = get_data_loader()

    # Get a test fund
    funds = loader.get_available_funds()
    test_scheme_code = funds['scheme_code'].iloc[0]

    min_date, max_date = loader.get_fund_date_range(test_scheme_code)

    assert min_date is not None, "min_date is None"
    assert max_date is not None, "max_date is None"
    assert min_date <= max_date, "min_date should be <= max_date"

    print(f"✅ Fund {test_scheme_code} date range: {min_date} to {max_date}")


def test_get_benchmark_options():
    """Test getting benchmark options"""
    loader = get_data_loader()
    benchmarks = loader.get_benchmark_options()

    assert benchmarks is not None, "get_benchmark_options returned None"
    assert isinstance(benchmarks, list), "get_benchmark_options should return list"
    assert len(benchmarks) > 0, "No benchmarks returned"

    print(f"✅ Found {len(benchmarks)} benchmarks")
    print(f"   Sample benchmarks: {benchmarks[:3]}")


def test_get_benchmark_date_range():
    """Test getting benchmark date range"""
    loader = get_data_loader()

    # Get available benchmarks
    benchmarks = loader.get_benchmark_options(index_type='PRICE')
    assert len(benchmarks) > 0, "No PRICE benchmarks available"

    test_benchmark = benchmarks[0]
    min_date, max_date = loader.get_benchmark_date_range(test_benchmark, 'PRICE')

    assert min_date is not None, "min_date is None"
    assert max_date is not None, "max_date is None"
    assert min_date <= max_date, "min_date should be <= max_date"

    print(f"✅ Benchmark {test_benchmark} date range: {min_date} to {max_date}")


def test_load_benchmark_data():
    """Test loading benchmark data"""
    loader = get_data_loader()

    # Get available benchmarks
    benchmarks = loader.get_benchmark_options(index_type='PRICE')
    assert len(benchmarks) > 0, "No PRICE benchmarks available"

    test_benchmark = benchmarks[0]
    bench_series = loader.load_benchmark_data(
        index_name=test_benchmark,
        index_type='PRICE',
        start_date='2024-01-01',
        end_date='2024-12-31'
    )

    assert bench_series is not None, "load_benchmark_data returned None"
    assert isinstance(bench_series, pd.Series), "load_benchmark_data should return Series"
    assert len(bench_series) > 0, "No benchmark data returned"
    assert bench_series.name == 'value', "Series should be named 'value'"

    print(f"✅ Loaded benchmark data for {test_benchmark}")
    print(f"   Date range: {bench_series.index[0]} to {bench_series.index[-1]}")
    print(f"   Data points: {len(bench_series)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MKTDATALOADER UNIT TESTS")
    print("="*70 + "\n")

    test_get_data_loader()
    test_connection()
    test_get_available_funds()
    test_load_fund_data_wide()
    test_load_fund_data_long()
    test_get_data_date_range()
    test_get_fund_date_range()
    test_get_benchmark_options()
    test_get_benchmark_date_range()
    test_load_benchmark_data()

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70 + "\n")
