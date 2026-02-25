"""
Fetch Asset Price Data from Yahoo Finance
==========================================

This script fetches historical asset price data from Yahoo Finance
and saves it to the raw data directory.

Assets included:
- ^GSPC: S&P 500 Index (25+ years of history, back to 2001)
- GC=F: Gold Futures (continuous contract, back to 2001)
- BTC-USD: Bitcoin Price (from inception ~2014)

Yahoo Finance provides free historical daily prices with extensive history.

Setup:
    1. Install libraries: pip install yfinance pandas
    2. Run: python code/fetch_asset_prices.py
"""

import sys
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from config_paths import RAW_DATA_DIR


# Dictionary of Yahoo Finance tickers and their configurations
ASSET_CONFIG = {
    '^GSPC': {
        'name': 'S&P 500 Index',
        'filename': 'sp500.csv',
        'column': 'sp500_index',
        'years': 25  # Fetch 25 years of history
    },
    'GC=F': {
        'name': 'Gold Futures (Continuous Contract)',
        'filename': 'gold_price.csv',
        'column': 'gold_price_usd',
        'years': 25  # Fetch 25 years of history
    },
    'BTC-USD': {
        'name': 'Bitcoin Price',
        'filename': 'bitcoin_price.csv',
        'column': 'bitcoin_price_usd',
        'years': 25  # Will get all available data (Bitcoin started ~2014)
    }
}


def fetch_asset_data(ticker, years=25):
    """
    Fetch asset price data from Yahoo Finance.
    
    Parameters:
        ticker (str): Yahoo Finance ticker symbol
        years (int): Number of years of historical data to fetch
    
    Returns:
        pd.DataFrame: Asset price data with date and price columns
    """
    print(f"\n  Fetching {ticker}...")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365 + years//4)  # Account for leap years
    
    try:
        # Create ticker object
        asset = yf.Ticker(ticker)
        
        # Fetch historical data
        df = asset.history(start=start_date, end=end_date)
        
        if df.empty:
            raise RuntimeError(f"No data returned for {ticker}")
        
        # Clean and prepare data
        df = df.reset_index()
        df = df[['Date', 'Close']].copy()
        df.columns = ['date', 'price']
        
        # Remove timezone info for consistency
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        print(f"    ✓ Fetched {len(df)} observations")
        print(f"      Range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"      Latest price: ${df['price'].iloc[-1]:,.2f}")
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {ticker}: {str(e)}")


def save_asset_data(df, filename, column_name):
    """
    Save asset price data to raw data directory.
    
    Parameters:
        df (pd.DataFrame): Asset price data
        filename (str): Output filename
        column_name (str): Name for the price column
    """
    # Rename price column to specific asset name
    df = df.rename(columns={'price': column_name})
    
    output_path = RAW_DATA_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"    ✓ Saved to: {output_path.name}")


def fetch_all_assets():
    """
    Fetch all asset prices and save to raw data directory.
    
    Returns:
        dict: Dictionary of fetched dataframes
    """
    print("\n" + "=" * 70)
    print("Yahoo Finance Asset Price Data Fetcher")
    print("=" * 70)
    
    results = {}
    errors = []
    
    for ticker, config in ASSET_CONFIG.items():
        try:
            print(f"\nProcessing: {config['name']}")
            
            # Fetch data
            df = fetch_asset_data(ticker, years=config['years'])
            
            # Save data
            save_asset_data(df, config['filename'], config['column'])
            
            results[ticker] = {
                'dataframe': df,
                'config': config,
                'success': True
            }
            
        except Exception as e:
            error_msg = f"Error fetching {ticker} ({config['name']}): {str(e)}"
            print(f"    ❌ {error_msg}")
            errors.append(error_msg)
            results[ticker] = {
                'config': config,
                'success': False,
                'error': str(e)
            }
    
    return results, errors


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("FETCHING ASSET PRICES FROM YAHOO FINANCE")
    print("=" * 70)
    
    try:
        # Fetch all assets
        results, errors = fetch_all_assets()
        
        # Summary
        print("\n" + "=" * 70)
        print("FETCH SUMMARY")
        print("=" * 70)
        
        successful = sum(1 for r in results.values() if r['success'])
        total = len(results)
        
        print(f"\nSuccessfully fetched: {successful}/{total} assets")
        
        if successful > 0:
            print("\n✓ Successful fetches:")
            for ticker, result in results.items():
                if result['success']:
                    config = result['config']
                    df = result['dataframe']
                    print(f"  • {config['name']:25s} → {config['filename']:25s} ({len(df):,} rows)")
        
        if errors:
            print("\n❌ Errors encountered:")
            for error in errors:
                print(f"  • {error}")
        
        print("\n" + "=" * 70)
        print(f"✓ Asset price data saved to: {RAW_DATA_DIR}")
        print("=" * 70 + "\n")
        
        return 0 if not errors else 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
