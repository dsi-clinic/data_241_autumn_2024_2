import csv
import os
import sqlite3
import io
from pandas import DataFrame

import logging
import zipfile
from os import listdir
from pathlib import Path


def execute_sql_command(conn, sql_query):  #Untouched
    cur = conn.cursor()
    cur.execute(sql_query)
    conn.commit()
    return None


#Loading in the whole table (to replace pandas loading in routes)
def load_data():
  conn = create_db_connection()
  df = DataFrame(conn.fetchall())
  df.columns = resoverall.keys()
  return df



# TASK 1
'''
make db_create: This creates the database file (stocks.db) and associated tables.
This creates a database file (but only if one does not exist, it should raise an error if the file exists)
This should also create a table (stocks) for storing the stocks data.
Should be placed in a location that makes sense given your overall file structure


Should be in a location that is mounted as a volume so that when your container is destroyed the data is not lost.
*** ^ Someone understand this please
'''
#___________________________________________


def create_stocks_table(conn):
    """Create a stocks table"""
    create_stocks = """
    CREATE TABLE stocks (
        Symbol TEXT PRIMARY KEY,
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



def create_stocks_db():
    """Creates an empty SQLite database at the specified path.
    Errors out if a database already exists at that path.

    """
    #CREATES IN data FOLDER / CAN CHANGE BUT PLEASE EDIT ALL INSTANCES OF db_path
    #___________________________________________
    db_path = "/app/src/data/" + "stocks.db"
    #___________________________________________


    # Check if the file already exists
    if os.path.exists(db_path):
        raise FileExistsError(f"Database already exists at {db_path}")

    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    print(f"Connected to Database")


    #CREATES TABLE IN DB
    #___________________________________________
    create_stocks_table(conn)
    print(f"TABLE created in {db_path}")
    #___________________________________________


    # Close the connection
    conn.close()

    return True

#___________________________________________




# TASK 2
"""
this loads the data from zip files to the table in stocks.
"""
#___________________________________________

def load_csv_to_db(conn, zip_path, table_name):
    """Load a CSV file into an existing SQLite table.

    Args:
        zip_path: Path to the CSV file
        conn: SQLite connection
        table_name: Name of the existing table
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        file_list = zf.namelist()
        #For each csv file in zip file
        for csv_file in file_list:
            with zf.open(csv_file) as f:
                text_file = io.TextIOWrapper(f, encoding="utf-8")
                reader = csv.reader(text_file)
                headers = next(reader)[0:]  # Get column names

                # Prepare INSERT statement
                placeholders = ",".join("?" for _ in headers)
                insert_sql = (
                    f"INSERT INTO {table_name} ({','.join(headers)})"
                    f" VALUES ({placeholders})"
                )
                # Insert all rows
                cur = conn.cursor()
                # import pdb; pdb.set_trace()
                cur.executemany(insert_sql, reader)
                conn.commit()
            print(f"Loaded {cur.rowcount} rows to {table_name} successfully")
            return True

def create_db_connection():
    """Sqlite specific connection function
    takes in the db_path
    """
    db_path = "/app/src/data/" + "stocks.db"
    if not os.path.exists(db_path):
        raise FileExistsError(f"Database does not exist at: {db_path}")

    conn = sqlite3.connect(db_path)
    return conn


def load_all_stock_data():
    """ LOADS STOCK DATA INTO TABLE
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
                return

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

#___________________________________________


#TASK 3
"""
this deletes the database file.
"""
#___________________________________________

def rm_db():
    """Delete the Database file
    not recoverable, be careful
    """
    db_path = "/app/src/data/" + "stocks.db"

    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"Database at {db_path} removed")

    return None

#___________________________________________

#Task 4
"""
this deletes the sqlite database file and reloads the data.
In other words it should run the rm, create and load commands in order.
If the database does not already exist it should not return an error
"""
#___________________________________________

def db_clean():
  rm_db()
  create_stocks_db()
  load_all_stock_data()
  return None

#___________________________________________
