"""Creates,Removes,Loads,Fetches Database Data"""

import csv
import io
import logging
import sqlite3
import zipfile
from os import listdir
from pathlib import Path


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


def execute_stock_q(query: str):
    """Executes a stock-related SQL query.

    Args:
        query: SQL query string to execute.

    Returns:
        Cursor object after query execution.
    """
    cursor = sqlite3.connect("/app/src/data/stocks.db").cursor()
    cursor.execute(query)
    return cursor


def create_stocks_table(conn):
    """Create a stocks table

    Returns:
            None
    """
    create_stocks = """
    CREATE TABLE stocks (
        market TEXT,
        Symbol TEXT,
        Date TEXT,
        Open REAL,
        High REAL,
        Low REAL,
        Close REAL,
        Volume INTEGER
    )
    """
    execute_sql_command(conn, create_stocks)
    return


def create_accounts_table(conn: sqlite3.Connection):
    """Creates the 'accounts' table in the database.

    Args:
        conn: SQLite connection object.

    Returns:
        None
    """
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
    return 



def create_stocks_owned_table(conn):
    """Create a stocks_owned table

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

    return


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
    print(f"Stocks TABLE created in {db_path}")

    # _____________________________________________
    create_accounts_table(conn)
    print(f"Accounts TABLE created in {db_path}")

    create_stocks_owned_table(conn)
    print(f"Stocks Owned TABLE created in {db_path}")
    # ______________________________________________

    conn.close()

    return True


def load_csv_to_db(conn, zip_path, table_name):
    """Load a CSV file into an existing SQLite table.

    Args:
        zip_path: Path to the CSV file
        conn: SQLite connection
        table_name: Name of the existing table
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = zf.namelist()
        file_list = file_list[:2]
        for csv_file in file_list:
            with zf.open(csv_file) as f:
                text_file = io.TextIOWrapper(f, encoding="utf-8")
                reader = csv.reader(text_file)
                headers = next(reader)[0:]  # Get column names
                # Prepare INSERT statement
                placeholders = ",".join("?" for _ in headers)
                headers = ["market"] + headers

                if "NASDAQ" in str(csv_file):
                    insert_sql = (
                        f"INSERT INTO {table_name} ({','.join(headers)})"
                        f" VALUES ('NASDAQ',{placeholders})"
                    )
                if "NYSE" in str(csv_file):
                    insert_sql = (
                        f"INSERT INTO {table_name} ({','.join(headers)})"
                        f" VALUES ('NYSE',{placeholders})"
                    )

                cur = conn.cursor()
                cur.executemany(insert_sql, reader)
                conn.commit()

            print(f"Loaded {csv_file}")
            print(f"Loaded {cur.rowcount} rows to {table_name}")

    return True


def add_account(account_info):
    """Adds a new account to the database.

    Args:
        account_info (dict): Dictionary containing account details, 
            such as 'name'.

    Returns:
        None
    """
    conn = create_db_connection()
    query = """
    INSERT INTO accounts
    (name)
    VALUES
    (?)
    """
    params = (account_info["name"],)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()


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
    """LOADS STOCK DATA INTO TABLE

    Returns:
            None
    """
    try:
        data_path = "/app/src/data/raw_data/"
        table_name = "stocks"
        conn = create_db_connection()
        # All zip files
        all_files = [
            data_path + f
            for f in listdir(data_path)
            if Path(data_path + f).is_file()
        ]
        # For each zip file
        for zip_path in all_files:
            logging.info(f"Loading {zip_path.split('/')[-1]} data...")
            try:
                load_csv_to_db(conn, zip_path, table_name)

            except zipfile.BadZipFile:
                logging.error(f"Invalid zip file: {zip_path}")
                raise ValueError(f"Invalid zip file: {zip_path}") from None

            except Exception as e:
                logging.error(f"Error merging data from {zip_path}: {e}")
                raise RuntimeError(f"Error merging data: {e}") from None

        return

    except Exception as e:
        logging.error(f"Error loading stock data: {e}")
        raise RuntimeError(f"Error loading stock data: {e}") from None



def add_stocks_data(stock_data_info):
    """Adds stock data to the 'stocks_owned' table in the database.

    Args:
        stock_data_info (dict): Dictionary containing stock details, such as
            'account_id', 'symbol', 'purchase_date', 'sale_date', and
            'number_of_shares'.

    Returns:
        None
    """
    conn = create_db_connection()
    query = """
    INSERT INTO stocks_owned
    (account_id, symbol, purchase_date, sale_date, number_of_shares)
    VALUES
    (?, ?, ?, ?, ?)
    """
    params = (
        stock_data_info["account_id"],
        stock_data_info["symbol"],
        stock_data_info["purchase_date"],
        stock_data_info["sale_date"],
        stock_data_info["number_of_shares"],
    )
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()


def remove_stocks_data(stock_data_info):
    """Removes stock data from the 'stocks_owned' table in the database.

    Args:
        stock_data_info (dict): Dictionary containing stock details, such as
            'account_id', 'symbol', 'purchase_date', 'sale_date', and
            'number_of_shares'.

    Returns:
        None
    """
    conn = create_db_connection()
    delete_query = """
    DELETE FROM stocks_owned
    WHERE account_id = ?
    AND symbol = ?
    AND purchase_date = ?
    AND sale_date = ?
    AND number_of_shares = ?
    """
    params = (
        stock_data_info["account_id"],
        stock_data_info["symbol"],
        stock_data_info["purchase_date"],
        stock_data_info["sale_date"],
        stock_data_info["number_of_shares"],
    )
    cursor = conn.cursor()
    cursor.execute(delete_query, params)
    conn.commit()


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

    if Path(accounts_db_path).exists():
        Path(accounts_db_path).unlink()
    if Path(stocks_owned_db_path).exists():
        Path(stocks_owned_db_path).unlink()
    if Path(db_path).exists():
        Path(db_path).unlink()

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
