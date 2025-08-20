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
def generate_date_range(days_back=90):
    """
    Generate a list of dates for the last N days in YYYY-MM-DD format.
    
    Args:
        days_back: Number of days to go back from today
        
    Returns:
        List of date strings in YYYY-MM-DD format
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    return [date.strftime('%Y-%m-%d') for date in date_range]

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
def scrape_binder_analytics(days_back=3):
    """
    Scrape MyBinder analytics data for the last N days and return as DataFrame.
    
    Args:
        days_back: Number of days to scrape (default: 90)
        
    Returns:
        pandas DataFrame with all the analytics data
    """
    print(f"Scraping MyBinder analytics data for the last {days_back} days...")
    
    # Generate date range
    dates = generate_date_range(days_back)
    print(f"Will attempt to fetch data for {len(dates)} dates from {dates[0]} to {dates[-1]}")
    
    # Collect all data
    all_data = []
    failed_dates = []
    
    for i, date_str in enumerate(dates):
        if i > 0 and i % 10 == 0:
            print(f"Progress: {i}/{len(dates)} dates processed")
            time.sleep(1)  # Be respectful to the server
        
        data = fetch_jsonl_data(date_str)
        if data:
            # Add date column to each record
            for record in data:
                record['fetch_date'] = date_str
            all_data.extend(data)
        else:
            failed_dates.append(date_str)
    
    print(f"\nScraping complete!")
    print(f"Successfully fetched: {len(dates) - len(failed_dates)}/{len(dates)} dates")
    print(f"Total events collected: {len(all_data)}")
    
    if failed_dates:
        print(f"Failed dates: {failed_dates[:10]}{'...' if len(failed_dates) > 10 else ''}")
    
    # Convert to DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        return df
    else:
        print("No data collected - returning empty DataFrame")
        return pd.DataFrame()

# %%
def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Scrape MyBinder analytics data')
    parser.add_argument('--days', type=int, default=90, 
                       help='Number of days to scrape (default: 90)')
    
    # Only parse args if running as script, not in notebook
    if '__file__' in globals() and len(sys.argv) > 1:
        args = parser.parse_args()
        days_back = args.days
    else:
        days_back = 3  # Default for notebook usage
    
    return scrape_binder_analytics(days_back=days_back)

# Run the scraper
df = main()

# %%
# Drop a few columns that don't have useful information
df = df.drop(columns=["build_token", "schema", "ref", "status", "version", "fetch_date"])

# %%
# Save to parquet for efficient storage
if not df.empty:
    path_file = __file__ if "__file__" in globals() else "."
    path_build = Path(path_file).parent.parent / "_build"
    path_build.mkdir(exist_ok=True)
    path_out = path_build / "launches.parquet"
    df.to_parquet(path_out, index=False)
    print(f"Data saved to {path_out}")
