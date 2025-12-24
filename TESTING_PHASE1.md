# Phase 1 Performance Testing Guide

## What Was Optimized

Phase 1 implemented session-based computation caching to eliminate redundant calculations:
- **Metrics calculations**: Now cached in session state (calculated once, reused everywhere)
- **Annual returns resampling**: Cached per fund
- **Monthly returns resampling**: Cached per fund

## Expected Performance Improvements

| Scenario | Before | After (Expected) | Improvement |
|----------|--------|------------------|-------------|
| Initial Category Deepdive load (20 funds) | 12-15s | ~5s | **60% faster** |
| Changing chart widgets (e.g., metric selection) | 4-5s | ~2s | **50% faster** |
| Date range changes | 12-15s | ~5s | **60% faster** |
| Memory usage per session | 500MB+ | <200MB | **60% less** |

## Testing Steps

### 1. Start the Application

```bash
# Make sure you're on the feature_app_clean branch
git branch  # Should show: * feature_app_clean

# Run the app
uv run streamlit run app.py
```

### 2. Test Category Deepdive Page

#### Test Scenario A: Initial Load (20+ Funds)

1. Navigate to **Category Deepdive** page (from sidebar)
2. Select category filters:
   - **Scheme Type**: Equity
   - **Category**: Any category with 20+ funds (e.g., "Large Cap", "Multi Cap")
3. Keep default date range (last 3 years)
4. Click **"Load Selected Funds"**

**Measure:**
- Time from clicking "Load Selected Funds" to all charts displaying
- Use browser DevTools (F12) → Performance tab, or just use a stopwatch
- Note the time in the terminal/browser

**Expected Result:**
- Initial load should complete in **< 5 seconds** (down from 12-15s)
- All 5 distribution charts should appear
- No errors in console

#### Test Scenario B: Widget Interactions (Cache Verification)

1. After initial load completes, scroll down to **"Bubble Scatter Chart"** section
2. Change the dropdown selections:
   - X-axis metric: Change from CAGR to "Sharpe Ratio"
   - Y-axis metric: Change to "Volatility"
   - Size metric: Change to "Max Drawdown"

**Measure:**
- Time for chart to update after each dropdown change
- Should be nearly instant

**Expected Result:**
- Chart updates should be **< 1 second** (almost instant)
- No spinners or loading indicators
- Smooth, responsive interactions

#### Test Scenario C: Date Range Changes

1. In the sidebar, change the date range:
   - Move start date forward by 6 months
   - Or change period to "Last 1 Year"
2. Observe page reload

**Measure:**
- Time for entire page to reload with new date range

**Expected Result:**
- Page reload should complete in **< 5 seconds**
- All metrics recalculated and cached again

#### Test Scenario D: Cache Persistence (Session State)

1. After loading a category, switch to another page (e.g., Fund Universe)
2. Switch back to Category Deepdive
3. Keep the same selections (category, funds, dates)

**Measure:**
- Time to reload the page

**Expected Result:**
- Should be **instant or < 1 second** (data loaded from cache)
- No database queries or metric recalculations

### 3. Verify Cache is Working

#### Check Session State (Optional - Advanced)

Add this debug code to `pages/category_deepdive.py` temporarily (after line 210):

```python
# Debug: Show cache stats
from src.computation_cache import get_cache_stats
cache_stats = get_cache_stats()
st.sidebar.markdown("### 🔍 Cache Debug")
st.sidebar.json(cache_stats)
```

**Expected Output:**
```json
{
  "metrics_entries": 21,  // 20 funds + 1 benchmark
  "annual_returns_entries": 21,
  "monthly_returns_entries": 21,
  "total_entries": 63
}
```

### 4. Check for Regressions

Test that everything still works correctly:

✅ **Metrics are accurate**:
- Compare CAGR, Sharpe Ratio values with previous version
- Spot check 2-3 funds manually

✅ **All charts render correctly**:
- [ ] CAGR Distribution
- [ ] Annual Returns Distribution
- [ ] Volatility Distribution
- [ ] Sharpe Ratio Distribution
- [ ] Max Drawdown Distribution
- [ ] Equity Curves
- [ ] Annual Returns Table
- [ ] Correlation Heatmap
- [ ] Bubble Scatter Chart
- [ ] Rolling Metrics Chart
- [ ] Performance Ranking Grid

✅ **No console errors**:
- Open browser DevTools (F12) → Console
- Should see no red error messages

✅ **Metrics table displays correctly**:
- Scroll to bottom of page
- Verify fund metrics table shows all 20+ funds
- Verify benchmark metrics row appears

### 5. Performance Comparison Test

To see the actual improvement, you can test with/without cache:

**With Cache (Current Branch):**
```bash
# Already on feature_app_clean
uv run streamlit run app.py
# Test and record time
```

**Without Cache (Main Branch):**
```bash
# Switch to main branch temporarily
git checkout main
uv run streamlit run app.py
# Test same scenario and record time
```

**Then switch back:**
```bash
git checkout feature_app_clean
```

## Key Performance Indicators to Monitor

| Indicator | How to Measure | Target |
|-----------|---------------|--------|
| **Initial load time** | Stopwatch from "Load Funds" click to charts display | < 5 seconds |
| **Widget interaction** | Time for chart to update after dropdown change | < 1 second |
| **Date range change** | Time to reload entire page | < 5 seconds |
| **Memory usage** | Browser Task Manager (Shift+Esc in Chrome) | < 200MB |
| **Cache entries** | Use debug code above | ~3x number of funds |

## Common Issues & Solutions

### Issue: Page loads slowly (still 10+ seconds)

**Possible Causes:**
1. Cache not being used (check import statement)
2. Database query still slow (Phase 2 will fix this)
3. Network latency to R2 storage

**Solution:**
- Add debug print statements to verify cache is being hit
- Check `st.session_state.metrics_cache` size

### Issue: Errors about missing keys in session_state

**Possible Cause:**
- Cache initialization not working

**Solution:**
- Check that `get_cached_metrics()` properly initializes cache dict
- Verify imports are correct

### Issue: Charts show wrong data

**Possible Cause:**
- Stale cache from previous session

**Solution:**
- Clear cache using browser refresh (Ctrl+R or Cmd+R)
- Or clear Streamlit cache: Click hamburger menu → "Clear cache"

### Issue: Memory usage still high

**Possible Cause:**
- Phase 1 only addresses computation time, not data loading
- Phase 2 (Two-Tier Data Loading) will address memory

**Note:**
- Expected memory improvement in Phase 1: ~20-30%
- Full memory optimization comes in Phase 2

## Success Criteria

✅ Phase 1 is successful if:

1. **Initial load time < 5 seconds** (with 20+ funds)
2. **Widget interactions < 1 second**
3. **No functional regressions** (all charts work)
4. **No console errors**
5. **Cache entries populate** (visible in debug output)

If any criteria fails, report the issue before proceeding to Phase 2.

## Reporting Results

After testing, please provide:

1. **Performance measurements** (seconds for each scenario)
2. **Any errors encountered** (with screenshots if possible)
3. **Subjective experience** (does it feel faster?)
4. **Cache stats** (if you added debug code)

Example report:
```
✅ Initial load: 4.8s (was 13s) - 63% improvement
✅ Widget changes: 0.5s (was 4s) - 87% improvement
✅ No errors or regressions
✅ Cache showing 63 entries for 21 funds
🎉 Phase 1 successful - ready for Phase 2!
```

## Next Steps After Testing

If Phase 1 tests successfully:
- ✅ Commit results to feature_app_clean branch
- ✅ Proceed to Phase 2: Two-Tier Data Loading Cache (20% additional improvement)

If Phase 1 has issues:
- 🔧 Debug and fix issues before Phase 2
- 🔍 Review implementation against plan
- 💬 Discuss findings and adjustments needed
