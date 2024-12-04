"""Creates,Removes,Loads,Fetches Database Data"""

import csv
import io
import logging
import sqlite3
import zipfile
from os import listdir
from pathlib import Path
from stock_app.api.logger_utils.custom_logger import custom_logger
import time
from datetime import datetime, timedelta

DB_PATH = "/app/src/data/stocks.db"


def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return conn


def execute_sql_command(conn, sql_query, variables=None):
    """Performs SQL command

    Returns:
            None
    """
    cur = conn.cursor()
    if variables is None:
        cur.execute(sql_query)
    else:
        cur.execute(sql_query, variables)
    conn.commit()
    return None


def execute_stock_q(query: str, parameter=None, fetch_all=True):
    """Executes a stock-related delete SQL query.

    Args:
        query: SQL query string to execute.
        parameter: query parameter
        fetch_all: fetch type

    Returns:
        Cursor object after query execution.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute parameter
        if parameter is None:
            cursor.execute(query)
        else:
            cursor.execute(query, parameter)

        # Handle SELECT queries
        if query.strip().upper().startswith("SELECT"):
            if fetch_all:
                return cursor.fetchall()  # Fetch all rows
            else:
                return cursor.fetchone()  # Fetch a single row
        else:
            # Commit changes for non-SELECT queries
            conn.commit()

        return cursor

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from None

    finally:
        conn.close()


# ___________________________________________________________________


def create_stocks_table(conn):
    """Create a stocks table

    Returns:
            None
    """
    create_stocks = """
    CREATE TABLE stocks (
        market TEXT,
        Symbol TEXT,
        Date Date,
        Open REAL,
        High REAL,
        Low REAL,
        Close REAL,
        Volume INTEGER
    )
    """
    execute_sql_command(conn, create_stocks)
    custom_logger.debug("'stocks' table created successfully.")
    return


# ________________________________________________________
# ADDED THIS to create accounts table


def create_accounts_table(conn):
    """Creates Accounts table"""
    create_accounts = """
    CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
    )
    """
    create_index = """
    CREATE UNIQUE INDEX id
    ON accounts (id)
    """
    execute_sql_command(conn, create_accounts)
    execute_sql_command(conn, create_index)
    custom_logger.debug("'accounts' table created successfully.")

    return


def create_stocks_owned_table(conn):
    """Create the 'stocks_owned' table.

    Args:
        conn (sqlite3.Connection): Database connection.

    Returns:
        None
    """
    create_stocks_owned = """
    CREATE TABLE stocks_owned (
        account_id INTEGER,
        symbol TEXT NOT NULL,
        purchase_date DATE NOT NULL,
        sale_date DATE NOT NULL,
        number_of_shares INTEGER NOT NULL
    )
    """
    execute_sql_command(conn, create_stocks_owned)
    custom_logger.debug("'stocks_owned' table created successfully.")
    


# _____________________________________________________________


def create_stocks_db():
    """Creates an empty SQLite database at the specified path.

    Errors out if a database already exists at that path.
    """
    db_path = "/app/src/data/" + "stocks.db"
    if Path(db_path).exists():
        raise FileExistsError(f"Database already exists at {db_path}")

    conn = sqlite3.connect(db_path)
    print("Connected to Database")

    create_stocks_table(conn)

    # _____________________________________________
    create_accounts_table(conn)

    create_stocks_owned_table(conn)
    # ______________________________________________

    conn.close()

    return True


def load_csv_to_db(conn, zip_path, table_name):
    """Load a CSV file into an existing SQLite table, formatting the date column as needed.

    Args:
        zip_path: Path to the CSV file
        conn: SQLite connection
        table_name: Name of the existing table
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = zf.namelist()
        file_list = file_list[:10]  # Load only the first two files
        for csv_file in file_list:
            with zf.open(csv_file) as f:
                text_file = io.TextIOWrapper(f, encoding="utf-8")
                reader = csv.reader(text_file)
                headers = next(reader)[0:]  # Get column names


                # Identify the index of the 'date' column, if present
                date_index = None
                for i, header in enumerate(headers):
                    if 'date' in header.lower():  # case-insensitive match
                        date_index = i
                        break

                # Add 'market' as the first column in the headers
                headers = ["market"] + headers

                # Prepare the placeholders (one for each header)
                placeholders = ",".join("?" for _ in headers)


                if "NASDAQ" in str(csv_file):
                    insert_sql = (
                        f"INSERT INTO {table_name} ({','.join(headers)})"
                        f" VALUES ({placeholders})"
                    )
                elif "NYSE" in str(csv_file):
                    insert_sql = (
                        f"INSERT INTO {table_name} ({','.join(headers)})"
                        f" VALUES ({placeholders})"
                    )

                # Process each row and format the date column if needed
                rows_to_insert = []
                for row in reader:
                    if date_index is not None:
                        # Format the date column (example: from 'DD-Mon-YYYY' to 'YYYY-MM-DD')
                        try:
                            original_date = row[date_index]
                            date_obj = datetime.strptime(original_date, "%d-%b-%Y")  # Adjust format as needed
                            formatted_date = date_obj.strftime("%Y-%m-%d")
                            row[date_index] = formatted_date
                        except ValueError:
                            print(f"Skipping invalid date: {original_date}")
                            continue  # Skip this row if the date is invalid

                    # Prepend 'market' to the row
                    row_to_insert = ("nasdaq" if "NASDAQ" in str(csv_file) else "nyse", *row)

                    # Debugging: Check the length of the row and headers

                    if len(row_to_insert) != len(headers):
                        print("Mismatch in number of columns!")
                        continue  # Skip this row if there's a mismatch

                    rows_to_insert.append(row_to_insert)

                # Insert the rows into the database
                cur = conn.cursor()
                try:
                    cur.executemany(insert_sql, rows_to_insert)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing insert: {e}")
                    continue  # Skip this file and move to the next one

    return True



# __________________________________________________


def create_db_connection():
    """Sqlite specific connection function

    Returns:
            Connection to db_path
    """
    db_path = "/app/src/data/" + "stocks.db"
    if not Path(db_path).exists():
        raise FileExistsError(f"Database does not exist at: {db_path}")

    conn = sqlite3.connect(db_path)
    return conn


def load_all_stock_data():
    """Loads stock data into the database from ZIP files.

    Returns:
        None
    """
    try:
        data_path = "/app/src/data/raw_data/"
        table_name = "stocks"
        conn = create_db_connection()
        custom_logger.info("Starting to load all stock data.")

        all_files = [
            data_path + f
            for f in listdir(data_path)
            if Path(data_path + f).is_file()
        ]

        for zip_path in all_files:
            file_name = zip_path.split('/')[-1]
            custom_logger.info(f"Loading data from {file_name}...")

            start_time = time.time()
            try:
                load_csv_to_db(conn, zip_path, table_name)
            except zipfile.BadZipFile:
                custom_logger.error(f"Invalid ZIP file: {zip_path}")
                raise ValueError(f"Invalid ZIP file: {zip_path}") from None
            except Exception as e:
                custom_logger.error(f"Error processing data from {zip_path}: {e}")
                raise RuntimeError(f"Error processing data: {e}") from None
            finally:
                duration = time.time() - start_time
                custom_logger.debug(f"Loaded data from {file_name} in {duration:.2f} seconds.")

        custom_logger.info("All stock data loaded successfully.")
    except Exception as e:
        custom_logger.error(f"Error loading all stock data: {e}")
        raise RuntimeError(f"Error loading all stock data: {e}") from None



# In the UTILS


def rm_db():
    """Delete the Database files

    Returns:
        None
    """
    # Define paths for database files
    stocks_db_path = "/app/src/data/stocks.db"
    accounts_db_path = "/app/src/data/accounts.db"
    stocks_owned_db_path = "/app/src/data/stocks_owned.db"

    # Ensure each file path exists before attempting to delete
    for db_path in [stocks_db_path, accounts_db_path, stocks_owned_db_path]:
        path = Path(db_path)
        if path.exists() and path.is_file():
            path.unlink()
    # ______________________________________________________________
    if Path(accounts_db_path).exists():
        Path(accounts_db_path).unlink()
    if Path(stocks_owned_db_path).exists():
        Path(stocks_owned_db_path).unlink()
    if Path(db_path).exists():
        Path(db_path).unlink()
    # ______________________________________________________________
    print(f"Databases at {db_path} removed")

    return None


def db_clean():
    """Removes,Creates,Loads stock database

    Returns:
            None
    """
    rm_db()
    create_stocks_db()
    load_all_stock_data()
    return None
