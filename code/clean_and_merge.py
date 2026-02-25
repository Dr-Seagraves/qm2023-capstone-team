"""
Clean, Process, and Merge Economic Data (Extended History)
===========================================================

This script cleans all raw data files, extends the date range back to 2001,
and creates the final merged dataset ready for analysis.

Key features:
- Standardizes all data to monthly frequency
- Extends date range back to February 2001 (start of gold data)
- Handles Bitcoin missing values (didn't exist before 2014)
- Saves both processed individual files and final merged dataset

Usage:
    python code/create_final_dataset.py
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR, FINAL_DATA_DIR


def load_and_clean_dataset(filename, date_col='date', value_col=None, freq='infer'):
    """
    Load and clean a single dataset.
    
    Parameters:
        filename (str): Name of CSV file in raw data directory
        date_col (str): Name of date column
        value_col (str): Name of value column (if None, uses second column)
        freq (str): Original frequency ('D', 'M', 'Q', or 'infer')
    
    Returns:
        tuple: (pd.DataFrame, str) - Cleaned dataframe with DatetimeIndex and value column name
    """
    filepath = RAW_DATA_DIR / filename
    
    print(f"  Loading {filename}...")
    df = pd.read_csv(filepath)
    
    # Convert date column to datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Set date as index
    df = df.set_index(date_col)
    
    # Get value column name
    if value_col is None:
        value_col = df.columns[0]
    
    # Keep only the value column
    df = df[[value_col]]
    
    # Check for missing values in raw data
    missing_count = df[value_col].isna().sum()
    if missing_count > 0:
        print(f"    ⚠ Found {missing_count} missing values")
    
    # Remove rows with missing dates or values
    df = df.dropna()
    
    # Sort by date
    df = df.sort_index()
    
    # Infer frequency if needed
    if freq == 'infer':
        freq = pd.infer_freq(df.index)
    
    print(f"    Frequency: {freq}, Range: {df.index.min().date()} to {df.index.max().date()}, Rows: {len(df)}")
    
    return df, value_col


def resample_to_monthly(df, value_col, method='last'):
    """
    Resample data to monthly frequency.
    
    Parameters:
        df (pd.DataFrame): Input dataframe with DatetimeIndex
        value_col (str): Name of value column
        method (str): Resampling method ('last', 'mean', 'sum', 'ffill')
    
    Returns:
        pd.DataFrame: Monthly resampled dataframe
    """
    if method == 'last':
        df_monthly = df.resample('ME').last()
    elif method == 'mean':
        df_monthly = df.resample('ME').mean()
    elif method == 'sum':
        df_monthly = df.resample('ME').sum()
    elif method == 'ffill':
        # For quarterly data, forward fill to monthly
        df_monthly = df.resample('ME').ffill()
    else:
        raise ValueError(f"Unknown resampling method: {method}")
    
    return df_monthly


def process_all_datasets():
    """
    Process all raw datasets and save to processed directory.
    
    Returns:
        dict: Dictionary of processed dataframes
    """
    print("\n" + "=" * 70)
    print("DATA CLEANING AND PROCESSING (EXTENDED TO 2001)")
    print("=" * 70 + "\n")
    
    processed_data = {}
    missing_value_report = []
    
    # Define dataset configurations
    # Format: (filename, final_column_name, resampling_method)
    datasets = [
        # Monetary aggregates (monthly)
        ('M1.csv', 'm1_billions', None),
        ('M2.csv', 'm2_billions', None),
        
        # Interest rates (daily → monthly last)
        ('federal_funds_rate.csv', 'fed_funds_rate', 'last'),
        ('real_interest_rate_10y.csv', 'real_rate_10y', 'last'),
        ('yield_curve_slope.csv', 'yield_curve_slope', 'last'),
        ('bbb_spread.csv', 'bbb_spread', 'last'),
        
        # Inflation (monthly)
        ('pce.csv', 'pce_index', None),
        ('cpi.csv', 'cpi_median', None),
        
        # Real economy (quarterly → monthly forward fill, monthly)
        ('gdp.csv', 'gdp_billions', 'ffill'),
        ('unemployment_rate.csv', 'unemployment_rate', None),
        
        # Asset prices (daily/monthly → monthly last)
        ('home_price_index.csv', 'home_price_index', None),
        ('sp500.csv', 'sp500_index', 'last'),
        ('gold_price.csv', 'gold_price_usd', 'last'),
        ('bitcoin_price.csv', 'bitcoin_price_usd', 'last'),
        
        # Market indicators (daily → monthly mean or last)
        ('vix.csv', 'vix_index', 'mean'),
        ('epu_index.csv', 'epu_index', 'mean'),
        ('consumer_sentiment.csv', 'consumer_sentiment', None),
    ]
    
    print("Step 1: Loading and cleaning individual datasets\n")
    
    for filename, final_col_name, resample_method in datasets:
        try:
            # Load and clean
            df, original_col = load_and_clean_dataset(filename)
            
            # Check for missing values before resampling
            missing_before = df[original_col].isna().sum()
            if missing_before > 0:
                missing_value_report.append({
                    'dataset': filename,
                    'stage': 'raw',
                    'missing_count': missing_before,
                    'action': 'dropped'
                })
            
            # Resample if needed
            if resample_method is not None:
                print(f"    Resampling to monthly using method: {resample_method}")
                df = resample_to_monthly(df, original_col, resample_method)
            else:
                # Ensure it's on month-end frequency
                if not isinstance(df.index.freq, pd.offsets.MonthEnd) and df.index.freq != 'ME':
                    df = df.resample('ME').last()
            
            # Rename column
            df = df.rename(columns={original_col: final_col_name})
            
            # Check for missing values after resampling
            missing_after = df[final_col_name].isna().sum()
            if missing_after > 0:
                print(f"    ⚠ {missing_after} missing values after resampling")
                missing_value_report.append({
                    'dataset': filename,
                    'stage': 'after_resample',
                    'missing_count': missing_after,
                    'action': 'will_fill'
                })
            
            # Store processed data
            processed_data[final_col_name] = df
            
            print(f"    ✓ Processed: {len(df)} monthly observations\n")
            
        except Exception as e:
            print(f"    ❌ Error processing {filename}: {str(e)}\n")
            continue
    
    print("\n" + "=" * 70)
    print("Step 2: Determining date range (starting from gold data)\n")
    
    # Find earliest date from gold data (our anchor point)
    gold_start = processed_data['gold_price_usd'].index.min()
    print(f"Gold data starts: {gold_start.date()}")
    
    # Use this as the start date for all series
    earliest_start = gold_start
    
    # Find the latest common date
    latest_end = min([df.index.max() for df in processed_data.values()])
    
    print(f"\nFinal date range: {earliest_start.date()} to {latest_end.date()}")
    print(f"Total months: {len(pd.date_range(earliest_start, latest_end, freq='ME'))}\n")
    
    # Create common date range
    common_dates = pd.date_range(earliest_start, latest_end, freq='ME')
    
    print("=" * 70)
    print("Step 3: Aligning all datasets to common date range\n")
    
    # Align all datasets
    aligned_data = {}
    for col_name, df in processed_data.items():
        # Reindex to common dates
        df_aligned = df.reindex(common_dates)
        
        # For Bitcoin, keep NaN values before it existed (don't fill with fake data)
        if col_name == 'bitcoin_price_usd':
            # Bitcoin data starts around 2014, leave earlier values as NaN
            bitcoin_start = df.index.min()
            print(f"  {col_name}: Keeping NaN before {bitcoin_start.date()} (Bitcoin didn't exist)")
            # Only forward fill within the actual Bitcoin data range
            mask = df_aligned.index >= bitcoin_start
            df_aligned.loc[mask, col_name] = df_aligned.loc[mask, col_name].ffill()
        else:
            # For other series, fill missing values
            missing_count = df_aligned[col_name].isna().sum()
            if missing_count > 0:
                print(f"  {col_name}: {missing_count} missing values → forward/backward filling")
                # Forward fill, then backward fill for any remaining NaNs at the start
                df_aligned[col_name] = df_aligned[col_name].ffill().bfill()
                
                # Check if still missing after filling
                still_missing = df_aligned[col_name].isna().sum()
                if still_missing > 0:
                    print(f"    ⚠ WARNING: {still_missing} values still missing after fill!")
                    missing_value_report.append({
                        'dataset': col_name,
                        'stage': 'final',
                        'missing_count': still_missing,
                        'action': 'STILL_MISSING'
                    })
        
        aligned_data[col_name] = df_aligned
    
    return aligned_data, common_dates, missing_value_report


def save_datasets(aligned_data, common_dates, missing_value_report):
    """
    Save processed individual files and create final merged dataset.
    
    Parameters:
        aligned_data (dict): Dictionary of aligned dataframes
        common_dates (pd.DatetimeIndex): Common date range
        missing_value_report (list): List of missing value reports
    """
    print("\n" + "=" * 70)
    print("Step 4: Saving processed individual datasets\n")
    
    # Save individual processed datasets
    for col_name, df in aligned_data.items():
        output_file = PROCESSED_DATA_DIR / f"{col_name}.csv"
        df.to_csv(output_file)
        print(f"  ✓ Saved: {output_file.name}")
    
    print("\n" + "=" * 70)
    print("Step 5: Creating final merged dataset\n")
    
    # Create merged dataset
    merged_df = pd.concat(aligned_data.values(), axis=1)
    merged_df.index.name = 'date'
    
    # Save merged dataset to FINAL directory
    merged_file = FINAL_DATA_DIR / "merged_economic_data.csv"
    merged_df.to_csv(merged_file)
    
    print(f"  ✓ Final merged dataset created: {merged_file.name}")
    print(f"    Location: {merged_file}")
    print(f"    Shape: {merged_df.shape} (rows: {merged_df.shape[0]}, columns: {merged_df.shape[1]})")
    print(f"    Date range: {merged_df.index.min().date()} to {merged_df.index.max().date()}")
    
    # Analyze missing values
    print(f"\n  Missing value analysis:")
    missing_by_col = merged_df.isna().sum()
    
    if missing_by_col.sum() == 0:
        print(f"    ✓ No missing values in any column!")
    else:
        print(f"    Total missing values: {missing_by_col.sum()}")
        print(f"\n    Missing values by column:")
        for col, count in missing_by_col[missing_by_col > 0].items():
            pct = (count / len(merged_df)) * 100
            print(f"      {col}: {count} ({pct:.1f}% of {len(merged_df)} months)")
    
    # Save missing value report
    if missing_value_report:
        print("\n" + "=" * 70)
        print("Missing Value Report\n")
        report_df = pd.DataFrame(missing_value_report)
        report_file = FINAL_DATA_DIR / "missing_values_report.csv"
        report_df.to_csv(report_file, index=False)
        print(f"  ✓ Report saved: {report_file.name}")
    
    return merged_df


def main():
    """Main execution function."""
    try:
        # Process all datasets
        aligned_data, common_dates, missing_value_report = process_all_datasets()
        
        # Save everything
        merged_df = save_datasets(aligned_data, common_dates, missing_value_report)
        
        print("\n" + "=" * 70)
        print("✓ DATA PROCESSING COMPLETE")
        print("=" * 70)
        print(f"\nFinal dataset summary:")
        print(f"  - Location: {FINAL_DATA_DIR / 'merged_economic_data.csv'}")
        print(f"  - Variables: {merged_df.shape[1]}")
        print(f"  - Monthly observations: {merged_df.shape[0]}")
        print(f"  - Date range: {merged_df.index.min().date()} to {merged_df.index.max().date()}")
        print(f"  - Years of data: {(merged_df.index.max() - merged_df.index.min()).days / 365.25:.1f}")
        
        # Bitcoin coverage
        bitcoin_data = merged_df['bitcoin_price_usd'].dropna()
        if len(bitcoin_data) > 0:
            print(f"\n  Bitcoin data coverage:")
            print(f"    - Available from: {bitcoin_data.index.min().date()}")
            print(f"    - Observations: {len(bitcoin_data)} months")
            print(f"    - Missing (pre-Bitcoin era): {merged_df['bitcoin_price_usd'].isna().sum()} months")
        
        print("\n  Data is ready for analysis!")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
