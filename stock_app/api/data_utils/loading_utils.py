"""Loads all stock data"""

import logging
import zipfile
import os
from os import listdir
from pathlib import Path

import pandas as pd


def merge_daily_stock_data(zip_path):
    """Merges all CSV files within a given zip file into a single DataFrame.

    Args:
        zip_path (str): Path to the zip file containing stock data.

    Returns:
        pd.DataFrame: Merged DataFrame with all CSVs appended.
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            file_list = zf.namelist()
            data = pd.read_csv(zf.open(file_list[0]))

            for csv_file in file_list[1:]:
                temp_df = pd.read_csv(zf.open(csv_file))
                data = pd.concat(
                    [data, temp_df], ignore_index=True, sort=False
                )

            # Add 'market' column based on file name
            if "NASDAQ" in zip_path:
                data["market"] = "NASDAQ"
            elif "NYSE" in zip_path:
                data["market"] = "NYSE"
            else:
                data["market"] = "Unknown"

        return data
    except zipfile.BadZipFile:
        logging.error(f"Invalid zip file: {zip_path}")
        raise ValueError(f"Invalid zip file: {zip_path}") from None
    except Exception as e:
        logging.error(f"Error merging data from {zip_path}: {e}")
        raise RuntimeError(f"Error merging data: {e}") from None


def load_all_stock_data():
    """Loads stock data from all zip files.

    Returns:
        pd.DataFrame: Combined DataFrame of stock data.
    """
    try:
        
        combined_df = pd.DataFrame()
        data_path = "/app/src/data/raw_data/"
        all_files = [
            data_path + f
            for f in listdir(data_path)
            if Path(data_path + f).is_file()
        ]

        for path in all_files:
            logging.info(f"Loading {path.split('/')[-1]} data...")
            year_df = merge_daily_stock_data(path)
            combined_df = pd.concat([combined_df, year_df], ignore_index=True)

        return combined_df
    except Exception as e:
        logging.error(f"Error loading stock data: {e}")
        raise RuntimeError(f"Error loading stock data: {e}") from None
