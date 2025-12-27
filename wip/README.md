# Work In Progress

This folder contains features and components that are under development and not yet ready for production release.

## Contents

### Multi-Page Application
- **app.py** - Multi-page Streamlit application with navigation between three pages
- **main.py** - Placeholder entry point

### Additional Pages
- **pages/category_deepdive.py** - Category-level analysis comparing multiple funds within a category
- **pages/fund_universe.py** - Fund universe explorer for portfolio-level analysis

### Exploration & Development
- **notebooks/** - Jupyter notebooks for data exploration and testing

## Running the WIP Multi-Page App

From the project root:
```bash
uv run streamlit run wip/app.py
```

## Note on Import Paths

All files in this folder use absolute imports from the project root:
- `from src.data_loader import ...`
- `from src.metrics import ...`
- `from utils.helpers import ...`

No import path changes are needed when moving files to/from this folder.

## Future Plans

These features are planned for future releases of Fund Investigator:
- Category Deepdive: Compare performance across funds in the same category
- Fund Universe: Portfolio-level analysis and fund screening
- Multi-page navigation: Unified platform for all analysis types

## Development Status

**Category Deepdive:**
- ✅ Equity curve visualization for multiple funds
- ✅ Fund selection and filtering
- ✅ Performance metrics comparison
- ⚠️  Performance monitor section (needs removal for production)

**Fund Universe:**
- ✅ Fund listing and filtering
- ✅ Basic metrics display
- ⚠️  Performance monitor section (needs removal for production)

**Multi-Page App:**
- ✅ Navigation between pages
- ✅ Shared data loader
- ✅ Consistent styling
