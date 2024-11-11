import argparse
import os

from loading_utils import (
    create_stocks_db,
    load_all_stock_data,
    rm_db,
    db_clean,
)



if __name__ == "__main__":
    command_list = ["db_create", "db_load", "db_rm", "db_clean"]
    parser = argparse.ArgumentParser(description="Manage the SQLite database.")

    parser.add_argument(
        "command", choices=command_list, help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "db_create":
        create_stocks_db()
    if args.command == "db_load":
        load_all_stock_data()
    if args.command == "db_rm":
        rm_db()
    if args.command == "db_clean":
        db_clean()
