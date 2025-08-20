# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # MyBinder Analytics Data Scraper
#
# This notebook scrapes JSONL files from archive.analytics.mybinder.org for the last 3 months
# and combines them into a single pandas DataFrame for analysis.

# %%
import pandas as pd
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import sys
import argparse

# %%

# %%
def fetch_jsonl_data(date_str, base_url="https://archive.analytics.mybinder.org"):
    """
    Fetch JSONL data for a specific date from the MyBinder analytics archive.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        base_url: Base URL for the analytics archive
        
    Returns:
        List of JSON objects from the JSONL file
    """
    url = f"{base_url}/events-{date_str}.jsonl"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse JSONL (each line is a JSON object)
        data = []
        for line in response.text.strip().split('\n'):
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse line in {date_str}: {line[:100]}")
                    continue
        
        print(f"✓ Fetched {len(data)} events for {date_str}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch data for {date_str}: {e}")
        return []

# %%
def load_existing_data(release_url="https://github.com/jupyterhub/binder-data/releases/download/latest/launches.parquet"):
    """
    Try to load existing data from the latest GitHub release.
    
    Returns:
        DataFrame with existing data, or empty DataFrame if not available
    """
    try:
        print(f"Downloading existing data from: {release_url}")
        df = pd.read_parquet(release_url)
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"✓ Loaded {len(df):,} existing records")
        print(f"Existing data range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        return df
        
    except Exception as e:
        print(f"✗ Could not load existing data: {e}")
        print("Will start fresh...")
        return pd.DataFrame()

# %%
def get_available_dates():
    """
    Get all available dates from the MyBinder analytics archive webpage.
    
    Returns:
        DataFrame with 'date' column containing available dates
    """
    try:
        print("Fetching available dates from archive webpage...")
        tables = pd.read_html("https://archive.analytics.mybinder.org/")
        
        if not tables:
            print("No tables found on webpage")
            return pd.DataFrame()
        
        # The first table contains the file listing with dates column
        files_df = tables[0]
        
        # Use the dates column directly and rename it
        available_df = files_df[['Date']].rename(columns={'Date': 'date'})
        
        print(f"✓ Found {len(available_df)} available dates on archive")
        return available_df
        
    except Exception as e:
        print(f"✗ Could not fetch available dates: {e}")
        return pd.DataFrame()

def get_missing_dates(existing_df, available_df):
    """
    Find dates that are available in the archive but missing from our dataset.
    
    Args:
        existing_df: DataFrame with existing data (has 'timestamp' column)
        available_df: DataFrame with available dates (has 'date' column)
        
    Returns:
        List of date strings that need to be fetched
    """
    if available_df.empty:
        print("No available dates found")
        return []
    
    if existing_df.empty:
        print("No existing data - will fetch all available dates")
        missing_dates = sorted(available_df['date'].tolist())
    else:
        # Get dates that exist in our dataset
        existing_dates = pd.DataFrame({
            'date': existing_df['timestamp'].dt.strftime('%Y-%m-%d')
        }).drop_duplicates()
        
        # Find missing dates by anti-joining
        missing_df = available_df[~available_df['date'].isin(existing_dates['date'])]
        missing_dates = sorted(missing_df['date'].tolist())
        
        print(f"Found {len(existing_dates)} unique dates in existing data")
    
    print(f"Found {len(missing_dates)} missing dates")
    if missing_dates:
        print(f"Date range to fetch: {missing_dates[0]} to {missing_dates[-1]}")
    
    return missing_dates

# %%
def scrape_binder_analytics():
    """
    Scrape MyBinder analytics data incrementally - first load existing data,
    then only fetch missing days based on what's available in the archive.
    
    Returns:
        pandas DataFrame with all the analytics data
    """
    print("Starting incremental data scraping...")
    
    # Step 1: Load existing data from GitHub release
    existing_df = load_existing_data()

    # Step 2: Get all available dates from the archive webpage
    available_df = get_available_dates()
    
    # Step 3: Determine which dates we are missing
    missing_dates = get_missing_dates(existing_df, available_df)
    
    if not missing_dates:
        print("No new data to fetch!")
        return existing_df
    
    print(f"Will fetch {len(missing_dates)} missing dates")
    
    # Step 3: Fetch missing data
    new_data = []
    failed_dates = []
    
    for i, date_str in enumerate(missing_dates):
        if i > 0 and i % 10 == 0:
            print(f"Progress: {i}/{len(missing_dates)} dates processed")
            time.sleep(1)  # Be respectful to the server
        
        data = fetch_jsonl_data(date_str)
        if data:
            new_data.extend(data)
        else:
            failed_dates.append(date_str)
    
    print(f"\nScraping complete!")
    print(f"Successfully fetched: {len(missing_dates) - len(failed_dates)}/{len(missing_dates)} dates")
    print(f"New events collected: {len(new_data)}")
    
    if failed_dates:
        print(f"Failed dates: {failed_dates[:10]}{'...' if len(failed_dates) > 10 else ''}")
    
    # Step 4: Combine existing and new data
    if new_data:
        new_df = pd.DataFrame(new_data)
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(new_df['timestamp']):
            new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
        
        print(f"New data shape: {new_df.shape}")
        
        if not existing_df.empty:
            # Combine with existing data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
            print(f"Combined dataset shape: {combined_df.shape}")
            print(f"Combined date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
            return combined_df
        else:
            return new_df
    else:
        print("No new data collected")
        return existing_df

# %%
def main():
    """Main function for CLI usage"""
    return scrape_binder_analytics()

# Run the scraper
df = main()

# %%
# Drop a few columns that don't have useful information (if they exist)
columns_to_drop = ["build_token", "schema", "ref", "status", "version", "fetch_date"]
existing_columns = [col for col in columns_to_drop if col in df.columns]
if existing_columns:
    df = df.drop(columns=existing_columns)
    print(f"Dropped columns: {existing_columns}")

# %%
# Save to parquet for efficient storage
if not df.empty:
    path_file = __file__ if "__file__" in globals() else "."
    path_build = Path(path_file).parent.parent / "_build"
    path_build.mkdir(exist_ok=True)
    path_out = path_build / "launches.parquet"
    df.to_parquet(path_out, index=False)
    print(f"Data saved to {path_out}")
