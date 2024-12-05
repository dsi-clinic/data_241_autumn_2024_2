"""Manage database operations: create, remove, load, and fetch data."""

import csv
import io
import sqlite3
import time
import zipfile
from datetime import datetime
from os import listdir
from pathlib import Path

from stock_app.api.logger_utils.custom_logger import custom_logger

DB_PATH = "/app/src/data/stocks.db"


def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return conn


def execute_sql_command(conn, sql_query, variables=None):
    """Execute an SQL command.

    Args:
        conn (sqlite3.Connection): Database connection.
        sql_query (str): SQL query string.
        variables (tuple, optional): Query parameters.

    Returns:
        None
    """
    with conn:
        cur = conn.cursor()
        cur.execute(sql_query, variables or ())


def execute_stock_q(query, parameter=None, fetch_all=True):
    """Execute stock-related SQL queries.

    Args:
        query (str): SQL query string.
        parameter (tuple, optional): Query parameters.
        fetch_all (bool): Whether to fetch all rows or a single row.

    Returns:
        list or sqlite3.Row: Query result.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, parameter or ())
        if query.strip().upper().startswith("SELECT"):
            return cur.fetchall() if fetch_all else cur.fetchone()
        conn.commit()
        return cur
    except sqlite3.Error as e:
        custom_logger.error(f"Database error: {e}")
        raise RuntimeError(f"Database error: {e}") from None
    finally:
        conn.close()


def create_table(conn, create_statement):
    """Create a table in the database.

    Args:
        conn (sqlite3.Connection): Database connection.
        create_statement (str): SQL statement to create the table.

    Returns:
        None
    """
    execute_sql_command(conn, create_statement)
    custom_logger.debug("Table created successfully.")


def create_stocks_db():
    """Create a SQLite database with required tables."""
    if Path(DB_PATH).exists():
        raise FileExistsError(f"Database already exists at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    custom_logger.info("Connected to database.")

    create_table(
        conn,
        """
        CREATE TABLE stocks (
            market TEXT,
            Symbol TEXT,
            Date DATE,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume INTEGER
        )
        """,
    )

    create_table(
        conn,
        """
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """,
    )

    create_table(
        conn,
        """
        CREATE TABLE stocks_owned (
            account_id INTEGER,
            symbol TEXT NOT NULL,
            purchase_date DATE NOT NULL,
            sale_date DATE NOT NULL,
            number_of_shares INTEGER NOT NULL
        )
        """,
    )

    conn.close()
    return True


def load_csv_to_db(conn, zip_path, table_name):
    """Load CSV data from a ZIP file into a SQLite table.

    Args:
        conn (sqlite3.Connection): Database connection.
        zip_path (str): Path to the ZIP file.
        table_name (str): Name of the table to load data into.

    Returns:
        bool: True if successful.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        for csv_file in zf.namelist()[:10]:  # Process only the first 10 files
            with zf.open(csv_file) as f:
                text_file = io.TextIOWrapper(f, encoding="utf-8")
                reader = csv.reader(text_file)
                headers = next(reader)

                date_index = next(
                    (
                        i
                        for i, header in enumerate(headers)
                        if "date" in header.lower()
                    ),
                    None,
                )

                headers = ["market"] + headers
                placeholders = ",".join("?" for _ in headers)
                market = "nasdaq" if "NASDAQ" in csv_file else "nyse"
                insert_sql = (
                    f"INSERT INTO {table_name} ({','.join(headers)}) "
                    f"VALUES ({placeholders})"
                )

                rows_to_insert = []
                for row in reader:
                    if date_index is not None:
                        try:
                            original_date = row[date_index]
                            row[date_index] = datetime.strptime(
                                original_date, "%d-%b-%Y"
                            ).strftime("%Y-%m-%d")
                        except ValueError:
                            custom_logger.warning(
                                f"Skipping invalid date: {original_date}"
                            )
                            continue

                    rows_to_insert.append((market, *row))

                cur = conn.cursor()
                try:
                    cur.executemany(insert_sql, rows_to_insert)
                    conn.commit()
                except Exception as e:
                    custom_logger.error(f"Error inserting rows: {e}")
                    continue
    return True


def load_all_stock_data():
    """Load all stock data from ZIP files into the database.

    Returns:
        None
    """
    data_path = "/app/src/data/raw_data/"
    table_name = "stocks"
    conn = get_db_connection()
    all_files = [
        f"{data_path}/{f}"
        for f in listdir(data_path)
        if Path(f"{data_path}/{f}").is_file()
    ]

    for zip_path in all_files:
        try:
            custom_logger.info(f"Loading data from {Path(zip_path).name}...")
            start_time = time.time()
            load_csv_to_db(conn, zip_path, table_name)
            duration = time.time() - start_time
            custom_logger.info(f"Loaded data in {duration:.2f} seconds.")
        except Exception as e:
            custom_logger.error(f"Error processing {Path(zip_path).name}: {e}")

    conn.close()


def rm_db():
    """Delete database files."""
    for db_file in ["stocks.db", "accounts.db", "stocks_owned.db"]:
        db_path = Path(f"/app/src/data/{db_file}")
        if db_path.exists():
            db_path.unlink()
            custom_logger.info(f"Deleted {db_file}")


def db_clean():
    """Remove, create, and load the database."""
    rm_db()
    create_stocks_db()
    load_all_stock_data()
