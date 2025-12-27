# Deploying Fund Investigator to Streamlit Cloud

## Prerequisites

1. GitHub account connected to Streamlit Cloud
2. Cloudflare R2 credentials (account ID, access key, secret key)
3. Repository pushed to GitHub

## Deployment Steps

### 1. Prepare Repository

Ensure these files are present:
- ✅ `requirements.txt` - Python dependencies
- ✅ `fundinvestigator_app.py` - App entry point
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ Updated `src/data_loader.py` - Supports Streamlit secrets

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select repository: `raro123/tearsheet`
4. Branch: `main`
5. Main file path: `fundinvestigator_app.py`
6. Python version: 3.11
7. Click "Advanced settings"

### 3. Configure Secrets in Streamlit Cloud

In the "Secrets" section of Advanced settings, paste:

```toml
# Cloudflare R2 Configuration
[r2]
account_id = "YOUR_R2_ACCOUNT_ID"
access_key_id = "YOUR_R2_ACCESS_KEY_ID"
secret_access_key = "YOUR_R2_SECRET_ACCESS_KEY"
endpoint_url = "https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com"
bucket_name = "financial-data-store"
region = "auto"

# Data Paths
[data]
nav_data_path = "mutual_funds/clean/nav_daily_growth_plan.parquet"
metadata_path = "mutual_funds/clean/scheme_metadata.parquet"
benchmark_data_path = "mutual_funds/clean/mf_benchmark_nifty.parquet"

# Cache Configuration
[cache]
ttl_hours = 24
```

**Replace placeholders** with actual values from your `.env` file.

### 4. Deploy

Click "Deploy" and wait for the app to build and start.

### 5. Verify Deployment

1. Check logs for R2 connection success
2. Verify fund data loads correctly
3. Test fund selection and analysis features

## Troubleshooting

### "Module not found" errors
- Check `requirements.txt` includes all dependencies
- Verify Python version matches (3.11)

### R2 Connection Failed
- Verify secrets are correctly configured in Streamlit Cloud UI
- Check R2 endpoint URL format
- Ensure R2 bucket and file paths are correct

### Data Loading Errors
- Check parquet file paths in secrets
- Verify R2 bucket permissions allow reading
- Check DuckDB httpfs extension loads correctly

## Local Development

For local development, use `.env` file (not committed):
```env
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
# etc.
```

The code automatically detects the environment and uses `.env` locally or `st.secrets` in cloud.

## Testing with Streamlit Secrets Locally

You can also test the Streamlit secrets approach locally using `.streamlit/secrets.toml`:

1. Ensure `.streamlit/secrets.toml` exists with your credentials
2. Temporarily rename or remove `.env` file
3. Run the app: `uv run streamlit run fundinvestigator_app.py`
4. The app should load data using secrets from `.streamlit/secrets.toml`

This simulates the cloud environment and verifies the secrets integration works correctly.
