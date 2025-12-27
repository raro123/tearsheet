"""Explore actual mktdata schema"""
import mktdata

print("="*80)
print("BENCHMARK DATA SAMPLE")
print("="*80)
bench_df = mktdata.query("SELECT * FROM mf_benhcmark_daily LIMIT 5")
print(bench_df)
print("\nColumns:", bench_df.columns.tolist())

print("\n" + "="*80)
print("NAV DATA SAMPLE")
print("="*80)
nav_df = mktdata.query("SELECT * FROM mf_nav_daily LIMIT 5")
print(nav_df)
print("\nColumns:", nav_df.columns.tolist())

print("\n" + "="*80)
print("SCHEMES DATA SAMPLE")
print("="*80)
schemes_df = mktdata.query("SELECT * FROM mf_schemes LIMIT 5")
print(schemes_df)
print("\nColumns:", schemes_df.columns.tolist())

print("\n" + "="*80)
print("BENCHMARK UNIQUE VALUES")
print("="*80)
unique_benchmarks = mktdata.query("""
    SELECT DISTINCT index_name, symbol, index_category
    FROM mf_benhcmark_daily
    ORDER BY index_name
    LIMIT 10
""")
print(unique_benchmarks)
