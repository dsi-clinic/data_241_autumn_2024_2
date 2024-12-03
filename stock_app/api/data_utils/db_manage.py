"""Manages and routes the make commands"""

import argparse
from logger_utils.custom_logger import custom_logger
import time
from loading_utils import (
    create_stocks_db,
    db_clean,
    load_all_stock_data,
    rm_db,
)

def execute_command(command_name, task):
    """Logs the start, end, and duration of a manage_db command."""
    custom_logger.info(f"Command '{command_name}' started.")
    start_time = time.time()
    
    try:
        task()  # Execute the command logic
    except Exception as e:
        custom_logger.error(f"Command '{command_name}' failed: {e}")
        raise
    finally:
        duration = time.time() - start_time
        custom_logger.info(f"Command '{command_name}' completed in {duration:.2f} seconds.")


if __name__ == "__main__":
    command_list = ["db_create", "db_load", "db_rm", "db_clean"]
    parser = argparse.ArgumentParser(description="Manage the SQLite database.")

    parser.add_argument(
        "command", choices=command_list, help="Command to execute"
    )

    args = parser.parse_args()

    # Route commands with logging
    if args.command == "db_create":
        execute_command("db_create", create_stocks_db)
    elif args.command == "db_load":
        execute_command("db_load", load_all_stock_data)
    elif args.command == "db_rm":
        execute_command("db_rm", rm_db)
    elif args.command == "db_clean":
        execute_command("db_clean", db_clean)

