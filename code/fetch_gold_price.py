"""
Fetch Gold Spot Price Data from Alpha Vantage
==============================================

This script fetches gold spot price data from the Alpha Vantage API
and saves it to the raw data directory.

Alpha Vantage provides daily, weekly, and monthly gold prices.

Setup:
    1. Install libraries: pip install requests pandas python-dotenv
    2. Get a free Alpha Vantage API key: https://www.alphavantage.co/support/#api-key
    3. Add ALPHAVANTAGE_API_KEY to your .env file
    4. Run: python code/fetch_gold_price.py
"""

import os
import sys
import pandas as pd
import requests
from config_paths import RAW_DATA_DIR


def get_api_key():
    """
    Get Alpha Vantage API key from environment variable or user input.
    
    Returns:
        str: Alpha Vantage API key
    """
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Check environment variable
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    
    # If not found, prompt user
    if not api_key:
        print("\n" + "=" * 70)
        print("ALPHA VANTAGE API KEY REQUIRED")
        print("=" * 70)
        print("\nGet a free API key at: https://www.alphavantage.co/support/#api-key")
        print("\nYou can either:")
        print("  1. Enter your API key now (copy/paste)")
        print("  2. Set ALPHAVANTAGE_API_KEY environment variable")
        print("  3. Add to .env file: ALPHAVANTAGE_API_KEY=your_key")
        print()
        api_key = input("Enter your Alpha Vantage API key: ").strip()
        
        if not api_key:
            raise ValueError("No API key provided. Exiting.")
    
    return api_key


def fetch_gold_data(api_key, interval='monthly'):
    """
    Fetch gold spot price data from Alpha Vantage.
    
    Parameters:
        api_key (str): Alpha Vantage API key
        interval (str): 'daily', 'weekly', or 'monthly' (default: monthly)
    
    Returns:
        pd.DataFrame: Gold price data with date and price columns
    """
    print("\nConnecting to Alpha Vantage API...")
    
    # Alpha Vantage endpoint for gold historical price
    url = 'https://www.alphavantage.co/query'
    
    params = {
        'function': 'GOLD_SILVER_HISTORY',
        'symbol': 'GOLD',
        'interval': interval,
        'apikey': api_key
    }
    
    print(f"Fetching gold spot price data ({interval})...")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Check for error messages
        if 'Error Message' in data:
            raise RuntimeError(f"API Error: {data['Error Message']}")
        if 'Note' in data:
            raise RuntimeError(f"API Limit: {data['Note']}")
        if 'Information' in data:
            raise RuntimeError(f"API Info: {data['Information']}")
        
        # Parse the response - Alpha Vantage GOLD_SILVER_HISTORY returns different formats
        # Check if it's the simple format with 'price' and 'timestamp'
        if 'price' in data and 'timestamp' in data:
            # Single data point format (current price)
            df = pd.DataFrame({
                'date': [pd.to_datetime(data['timestamp'])],
                'gold_price_usd': [float(data['price'])]
            })
        elif 'data' in data:
            # GOLD_SILVER_HISTORY returns data as a list
            data_list = data['data']
            dates = []
            prices = []
            
            for item in data_list:
                dates.append(pd.to_datetime(item['date']))
                # Try different possible key names for the price
                if 'value' in item:
                    prices.append(float(item['value']))
                elif 'price' in item:
                    prices.append(float(item['price']))
                elif 'close' in item:
                    prices.append(float(item['close']))
                else:
                    # Use first numeric value found
                    for v in item.values():
                        try:
                            prices.append(float(v))
                            break
                        except (ValueError, TypeError):
                            continue
            
            df = pd.DataFrame({
                'date': dates,
                'gold_price_usd': prices
            })
        else:
            # Try to find time series data
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key or 'time series' in key.lower():
                    time_series_key = key
                    break
            
            if time_series_key:
                time_series = data[time_series_key]
                dates = []
                prices = []
                
                for date_str, values in time_series.items():
                    dates.append(pd.to_datetime(date_str))
                    # Gold price is typically in the 'close' or 'price' field
                    price_key = '4. close' if '4. close' in values else 'price'
                    if price_key in values:
                        prices.append(float(values[price_key]))
                    else:
                        # If neither key exists, use the first numeric value
                        for v in values.values():
                            try:
                                prices.append(float(v))
                                break
                            except (ValueError, TypeError):
                                continue
                
                df = pd.DataFrame({
                    'date': dates,
                    'gold_price_usd': prices
                })
            else:
                raise RuntimeError(f"Unexpected API response format. Available keys: {list(data.keys())}")
        
        df = df.sort_values('date').reset_index(drop=True)
        
        print(f"✓ Successfully fetched {len(df)} observations")
        print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"  Latest gold price: ${df['gold_price_usd'].iloc[-1]:.2f}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch data from Alpha Vantage: {str(e)}")


def save_gold_data(df, filename='gold_price.csv'):
    """
    Save gold price data to raw data directory.
    
    Parameters:
        df (pd.DataFrame): Gold price data
        filename (str): Output filename
    """
    output_path = RAW_DATA_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"✓ Data saved to: {output_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("Alpha Vantage Gold Price Data Fetcher")
    print("=" * 70)
    
    try:
        # Get API key
        api_key = get_api_key()
        
        # Fetch data
        df = fetch_gold_data(api_key, interval='monthly')
        
        # Save data
        save_gold_data(df, filename='gold_price.csv')
        
        print("\n" + "=" * 70)
        print("✓ SUCCESS! Gold price data has been saved to data/raw/gold_price.csv")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
