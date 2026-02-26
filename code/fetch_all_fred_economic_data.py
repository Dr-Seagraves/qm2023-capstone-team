"""
Fetch Multiple Economic Data Series from FRED
==============================================

This script fetches multiple economic indicators from FRED and saves them
to the raw data directory.

Data series included:
- M1SL: M1 Money Stock
- M2SL: M2 Money Stock
- DFF: Federal Funds Rate
- REAINTRATREARAT10Y: 10-Year Real Interest Rate
- T10Y2Y: 10Y-2Y Treasury Yield Spread (yield curve slope)
- PCE: Personal Consumption Expenditures Price Index
- MEDCPIM158SFRBCLE: Median Consumer Price Index
- GDP: Gross Domestic Product
- UNRATE: Unemployment Rate
- CSUSHPISA: Case-Shiller U.S. National Home Price Index
- VIXCLS: CBOE Volatility Index (VIX)
- USEPUINDXD: US Economic Policy Uncertainty Index
- BAMLC0A4CBBB: ICE BofA BBB Corporate Bond Spread
- UMCSENT: University of Michigan Consumer Sentiment

Note: S&P 500 and Bitcoin are fetched from Yahoo Finance (see fetch_asset_prices.py)

Setup:
    1. Ensure libraries are installed: pip install fredapi pandas python-dotenv
    2. API key should be in .env file
    3. Run: python code/fetch_all_economic_data.py
"""

import os
import sys
import pandas as pd
from fredapi import Fred
from config_paths import RAW_DATA_DIR

# Dictionary of FRED series IDs and their descriptions
SERIES_CONFIG = {
    'M1SL': {
        'name': 'M1 Money Stock',
        'filename': 'M1.csv',
        'column': 'm1_billions'
    },
    'M2SL': {
        'name': 'M2 Money Stock',
        'filename': 'M2.csv',
        'column': 'm2_billions'
    },
    'DFF': {
        'name': 'Federal Funds Rate',
        'filename': 'federal_funds_rate.csv',
        'column': 'rate_percent'
    },
    'REAINTRATREARAT10Y': {
        'name': '10-Year Real Interest Rate',
        'filename': 'real_interest_rate_10y.csv',
        'column': 'real_rate_percent'
    },
    'T10Y2Y': {
        'name': '10Y-2Y Treasury Yield Spread',
        'filename': 'yield_curve_slope.csv',
        'column': 'spread_percent'
    },
    'PCE': {
        'name': 'Personal Consumption Expenditures Price Index',
        'filename': 'pce.csv',
        'column': 'pce_index'
    },
    'MEDCPIM158SFRBCLE': {
        'name': 'Median Consumer Price Index',
        'filename': 'cpi.csv',
        'column': 'cpi_index'
    },
    'GDP': {
        'name': 'Gross Domestic Product',
        'filename': 'gdp.csv',
        'column': 'gdp_billions'
    },
    'UNRATE': {
        'name': 'Unemployment Rate',
        'filename': 'unemployment_rate.csv',
        'column': 'rate_percent'
    },
    'CSUSHPISA': {
        'name': 'Case-Shiller U.S. National Home Price Index',
        'filename': 'home_price_index.csv',
        'column': 'index_value'
    },
    'VIXCLS': {
        'name': 'CBOE Volatility Index (VIX)',
        'filename': 'vix.csv',
        'column': 'vix_index'
    },
    'USEPUINDXD': {
        'name': 'US Economic Policy Uncertainty Index',
        'filename': 'epu_index.csv',
        'column': 'epu_index'
    },
    'BAMLC0A4CBBB': {
        'name': 'ICE BofA BBB Corporate Bond Spread',
        'filename': 'bbb_spread.csv',
        'column': 'spread_percent'
    },
    'UMCSENT': {
        'name': 'University of Michigan Consumer Sentiment',
        'filename': 'consumer_sentiment.csv',
        'column': 'sentiment_index'
    }
}


def get_api_key():
    """
    Get FRED API key from environment variable or .env file.
    
    Checks in the following order:
    1. .env file (production)
    2. .env.example file (fallback for development)
    3. User input (if neither file has the key)
    
    Returns:
        str: FRED API key
    """
    from dotenv import load_dotenv
    
    # Try to load from .env file first
    load_dotenv('.env')
    api_key = os.getenv('FRED_API_KEY')
    
    # If not found in .env, try .env.example as fallback
    if not api_key:
        load_dotenv('.env.example')
        api_key = os.getenv('FRED_API_KEY')
    
    # If still not found, prompt user
    if not api_key:
        print("\n" + "=" * 70)
        print("FRED API KEY REQUIRED")
        print("=" * 70)
        print("\nGet a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print()
        api_key = input("Enter your FRED API key: ").strip()
        
        if not api_key:
            raise ValueError("No API key provided. Exiting.")
    
    return api_key


def fetch_series(fred, series_id, series_name, start_date=None, end_date=None):
    """
    Fetch a single series from FRED.
    
    Parameters:
        fred: Fred API client
        series_id (str): FRED series ID
        series_name (str): Human-readable name
        start_date (str, optional): Start date
        end_date (str, optional): End date
    
    Returns:
        pd.Series: Time series data
    """
    print(f"  Fetching {series_name} ({series_id})...")
    try:
        data = fred.get_series(series_id, 
                              observation_start=start_date,
                              observation_end=end_date)
        print(f"    ✓ {len(data)} observations")
        return data
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return None


def save_series(data, filename, column_name):
    """
    Save series data to CSV.
    
    Parameters:
        data (pd.Series): Time series data
        filename (str): Output filename
        column_name (str): Name for the data column
    """
    if data is None or len(data) == 0:
        return False
    
    df = pd.DataFrame({
        'date': data.index,
        column_name: data.values
    }).reset_index(drop=True)
    
    output_path = RAW_DATA_DIR / filename
    df.to_csv(output_path, index=False)
    return True


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("FRED Economic Data Fetcher")
    print("=" * 70)
    print(f"\nFetching {len(SERIES_CONFIG)} economic data series...\n")
    
    try:
        # Get API key
        api_key = get_api_key()
        
        # Initialize FRED client
        print("\nConnecting to FRED API...")
        fred = Fred(api_key=api_key)
        
        # Fetch all series
        print("\nFetching data series:")
        results = {}
        for series_id, config in SERIES_CONFIG.items():
            data = fetch_series(fred, series_id, config['name'])
            if data is not None:
                results[series_id] = data
        
        # Save all series
        print("\nSaving data to files:")
        success_count = 0
        for series_id, data in results.items():
            config = SERIES_CONFIG[series_id]
            if save_series(data, config['filename'], config['column']):
                print(f"  ✓ {config['filename']}")
                success_count += 1
        
        print("\n" + "=" * 70)
        print(f"✓ SUCCESS! {success_count}/{len(SERIES_CONFIG)} series saved to data/raw/")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
