"""Creates,Removes,Loads,Fetches Database Data"""

import csv
import io
import logging
import sqlite3
import zipfile
from os import listdir
from pathlib import Path
import pandas as pd


def execute_sql_command(conn, sql_query):
    """Performs SQL command

    Returns:
            None
    """
    cur = conn.cursor()
    cur.execute(sql_query)
    conn.commit()
    return None


def execute_query_return_list_of_dicts_lm(conn, sql_query):
    """Low memory version of loading command command

    Returns:
            Dictionary list of SQL query
    """
    cursor = conn.cursor()
    cursor.execute(sql_query)
    description_info = cursor.description

    headers = [x[0] for x in description_info]
    return_dict_list = []

    while True:
        single_result = cursor.fetchone()

        if not single_result:
            break

        single_result_dict = dict(zip(headers, single_result))
        return_dict_list.append(single_result_dict)

    return return_dict_list

#CHANGED THIS TO STOCK DATA
#CHANGE FOR EACH ROUTE IN PULLIN IN DATA
#____________________________________________________________________
def load_stock_data():
    """Loading data into pandas DF

    Returns:
            Dataframe containing all of the stock data
    """
    print("Loading Data")
    conn = create_db_connection()
    query = """select market,
            Symbol,
            Date,
            Open,
            High,
            Low,
            Close,
            Volume
         from stocks
    """
    fetch_data = pd.DataFrame(
        execute_query_return_list_of_dicts_lm(conn, query)
    )
    return fetch_data


def load_account_data():
    """Loading data into pandas DF

    Returns:
            Dataframe containing all of the account data
    """
    print("Loading Data")
    conn = create_db_connection()
    query = """select id,
            name
         from accounts
    """
    fetch_data = pd.DataFrame(
        execute_query_return_list_of_dicts_lm(conn, query)
    )
    return fetch_data


def load_stocks_owned_data():
    """Loading data into pandas DF

    Returns:
            Dataframe containing all of the stocks_owned data
    """
    print("Loading Data")
    conn = create_db_connection()
    query = """select account_id,
            symbol,
            purchase_date,
            sale_date,
            number_of_shares
         from accounts
    """
    fetch_data = pd.DataFrame(
        execute_query_return_list_of_dicts_lm(conn, query)
    )
    return fetch_data

#___________________________________________________________________

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

#________________________________________________________
#ADDED THIS to create accounts table

def create_accounts_table(conn):

    create_accounts = """
    CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
    )
    """
    execute_sql_command(conn, create_accounts)
    return


def create_stocks_owned_table(conn):
    """Create a stocks_owned table

    Returns:
            None
    """

    create_stocks_owned = """
    CREATE TABLE IF NOT EXISTS stocks_owned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    shares_owned INTEGER NOT NULL,
    purchase_price REAL NOT NULL,
    purchase_date TEXT NOT NULL
);
    """
    execute_sql_command(conn, create_stocks_owned)
    return
#_____________________________________________________________


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

    #_____________________________________________
    create_accounts_table(conn)
    print(f"Accounts TABLE created in {db_path}")

    create_stocks_owned_table(conn)
    print(f"Stocks Owned TABLE created in {db_path}")
    #______________________________________________


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

#ADD ACCOUNT
#___________________________________________________
def add_account(account_info):
    conn = create_db_connection()
    query = """
    INSERT INTO accounts
    (account_name)
    VALUES
    (?)
    """

    params = (
        account_info["name"]
    )

    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
#__________________________________________________



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


import os
from pathlib import Path

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
    #______________________________________________________________
    if Path(accounts_db_path).exists():
        Path(accounts_db_path).unlink()
    if Path(stocks_owned_db_path).exists():
        Path(stocks_owned_db_path).unlink()
    if Path(db_path).exists():
        Path(db_path).unlink()
    #______________________________________________________________
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
