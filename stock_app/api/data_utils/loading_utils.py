"""Creates, Removes, Loads, Fetches Database Data."""

import csv
import io
import logging
import sqlite3
import zipfile
from os import listdir
from pathlib import Path

DB_PATH = "/app/src/data/stocks.db"


def get_db_connection():
    """Get a database connection.

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return conn


def execute_sql_command(conn, sql_query, variables=None):
    """Execute an SQL command.

    Args:
        conn (sqlite3.Connection): The database connection.
        sql_query (str): The SQL query to execute.
        variables (tuple, optional): Query parameters.

    Returns:
        None
    """
    cur = conn.cursor()
    if variables is None:
        cur.execute(sql_query)
    else:
        cur.execute(sql_query, variables)
    conn.commit()


def execute_stock_q(query: str, parameter=None, fetch_all=True):
    """Execute a stock-related SQL query.

    Args:
        query (str): The SQL query string to execute.
        parameter (tuple, optional): Query parameters. Defaults to None.
        fetch_all (bool): Whether to fetch all rows or a single row. 
            Defaults to True.

    Returns:
        list or sqlite3.Row: 
            Query results for SELECT queries, 
            or the cursor object for other queries.

    Raises:
        RuntimeError: If a database error occurs.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the query
        if parameter is None:
            cursor.execute(query)
        else:
            cursor.execute(query, parameter)

        # Handle SELECT queries
        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall() if fetch_all else cursor.fetchone()

        # Commit changes for non-SELECT queries
        conn.commit()
        return cursor

    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
        raise RuntimeError(f"Database error: {e}") from e

    finally:
        conn.close()


def load_all_stock_data():
    """Load stock data into the database.

    Returns:
        None

    Raises:
        RuntimeError: If an error occurs during data loading.
    """
    try:
        data_path = "/app/src/data/raw_data/"
        table_name = "stocks"
        conn = get_db_connection()

        # Collect all zip files in the data path
        all_files = [
            data_path + f
            for f in listdir(data_path)
            if Path(data_path + f).is_file()
        ]


        # Process each zip file
        for zip_path in all_files:
            logging.info("Loading %s data...", zip_path.split("/")[-1])
            try:
                load_csv_to_db(conn, zip_path, table_name)
            except zipfile.BadZipFile:
                logging.error("Invalid zip file: %s", zip_path)
                raise ValueError(f"Invalid zip file: {zip_path}") from None
            except Exception as e:
                logging.error("Error merging data from %s: %s", zip_path, e)
                raise RuntimeError(f"Error merging data: {e}") from e
    except Exception as e:
        logging.error("Error loading stock data: %s", e)
        raise RuntimeError(f"Error loading stock data: {e}") from e


def load_csv_to_db(conn, zip_path, table_name):
    """Load a CSV file into an existing SQLite table.

    Args:
        conn (sqlite3.Connection): The database connection.
        zip_path (str): Path to the CSV file.
        table_name (str): Name of the existing table.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = zf.namelist()[:2]  # Limit to first 2 files
        for csv_file in file_list:
            with zf.open(csv_file) as f:
                text_file = io.TextIOWrapper(f, encoding="utf-8")
                reader = csv.reader(text_file)
                headers = next(reader)

                # Add the "market" column and prepare the INSERT statement
                headers = ["market"] + headers
                placeholders = ",".join("?" for _ in headers)
                market = "NASDAQ" if "NASDAQ" in csv_file else "NYSE"
                insert_sql = (
                    f"INSERT INTO {table_name} ({','.join(headers)}) "
                    f"VALUES ('{market}',{placeholders})"
                )

                # Insert the data
                cur = conn.cursor()
                cur.executemany(insert_sql, reader)
                conn.commit()

            logging.info(
                "Loaded %s with %d rows to %s",
                csv_file,
                cur.rowcount,
                table_name,
            )

