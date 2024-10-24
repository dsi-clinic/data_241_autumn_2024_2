import os
import pandas as pd
import zipfile

def merge_daily_stock_data(zip_path):
    """
    Merges all CSV files within a given zip file into a single DataFrame.
    
    Args:
        zip_path (str): Path to the zip file containing stock data.

    Returns:
        pd.DataFrame: Merged DataFrame with all CSVs appended, with a 'market' column 
                      indicating NASDAQ or NYSE based on the zip file name.
                      
    Raises:
        FileNotFoundError: If the zip file is not found or invalid.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            csv_files = zf.namelist()
            merged_df = pd.read_csv(zf.open(csv_files[0]))
            
            for csv_file in csv_files[1:]:
                temp_df = pd.read_csv(zf.open(csv_file))
                merged_df = pd.concat([merged_df, temp_df], ignore_index=True, sort=False)
            
            # Add 'market' column based on file name
            if 'NASDAQ' in zip_path:
                merged_df['market'] = 'NASDAQ'
            elif 'NYSE' in zip_path:
                merged_df['market'] = 'NYSE'
            else:
                merged_df['market'] = 'Unknown'
                
        return merged_df
    except zipfile.BadZipFile:
        raise FileNotFoundError(f"Invalid zip file: {zip_path}")
    except Exception as e:
        raise RuntimeError(f"Error merging data: {e}")

def combine_data():
    """
    Combines NASDAQ and NYSE stock data and filters for BRK.A stock symbol.

    Process:
    1. Loads separate DataFrames for NASDAQ and NYSE using the merge_daily_stock_data function.
    2. Combines both DataFrames into a single DataFrame.
    3. Filters for BRK.A stock symbol.
    4. Finds the date where BRK.A had the highest 'Open' value.
    5. Counts total, NASDAQ, and NYSE rows.

    Returns:
        tuple: Total rows, NASDAQ rows, NYSE rows, and the BRK.A date with the highest 'Open'.
    """
    nasdaq_zip_path = './data/raw_data/NASDAQ_2019.zip'
    nyse_zip_path = './data/raw_data/NYSE_2019.zip'

    # Load data
    nasdaq_df = merge_daily_stock_data(nasdaq_zip_path)
    nyse_df = merge_daily_stock_data(nyse_zip_path)

    # Combine NASDAQ and NYSE data
    combined_df = pd.concat([nasdaq_df, nyse_df], ignore_index=True, sort=False)

    # Filter for BRK.A stock
    brk_a_df = combined_df[combined_df['Symbol'] == 'BRK.A']

    # Get the date where BRK.A had the highest 'Open' value
    if not brk_a_df.empty:
        brk_a_date = brk_a_df[brk_a_df['Open'] == max(brk_a_df['Open'])]['Date'].iloc[0]
    else:
        brk_a_date = None

    # Row counts
    total_rows = combined_df.shape[0]
    nasdaq_rows = nasdaq_df.shape[0]
    nyse_rows = nyse_df.shape[0]

    return total_rows, nasdaq_rows, nyse_rows, brk_a_date

if __name__ == "__main__":
    total_rows, nasdaq_rows, nyse_rows, brk_a_date = combine_data()

    # Print results
    print(f"Total Rows: {total_rows}")
    print(f"Nasdaq Rows: {nasdaq_rows}")
    print(f"NYSE Rows: {nyse_rows}")
    
    if brk_a_date:
        print(f"BRK.A Max Open Date: {brk_a_date}")
    else:
        print("No BRK.A data found.")
