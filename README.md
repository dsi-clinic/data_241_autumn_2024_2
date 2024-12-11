# data_241_autumn_2024_2
## Repository Setup Guide

To set up and run this repository, execute the following commands in your terminal:

- **`make build`**: Builds the Docker image from the Dockerfile in your repository.
- **`make interactive`**: Starts an interactive bash session with the current working directory mounted to `/app/src`.
- **`make notebook`**: Starts a Jupyter Notebook server with the current working directory mounted to `/app/src`, with ports properly configured for external access.
- **`make flask`**: Starts the Flask server, exposing port `4000` for API accessibility.
- **`make db_create`**: Creates an SQLite database `stocks.db`, with a `stocks` table in the `data` folder.
- **`make db_load`**: Loads data from zip files in `raw_data` into the SQLite database.
- **`make db_rm`**: Removes the `stocks.db` database.
- **`make db_clean`**: Removes, creates, and loads data into the SQLite database in one command.

---

## People

- **Anuj Agarwal**: 4th-year Undergraduate, Data Science major.
- **Disha Mohta**: 4th-year Undergraduate, Economics and Data Science major.
- **Ishani Raj**: 3rd-year Undergraduate, Computer Science major.
- **Ken Law**: 4th-year Undergraduate, MENG major.

---

## Folders and Files

### **data folder**
- Contains all project data.
- Includes a subfolder `raw_data` with NASDAQ and NYSE_2019 zip files from 2010-2020.

### **Dockerfile**
- Provides a blueprint for building a consistent, isolated environment for the application.
  - **Base Image**: Specifies a Python base image for the correct version.
  - **Dependencies**: Installs all required Python libraries from `requirements.txt`.
  - **Directory Setup**: Configures the `/app/src` directory for code execution.
  - **Entrypoint**: Default configuration for running commands like `make flask` or `make notebook`.

### **Makefile**
- Automates common setup and execution tasks:
  - `make build`: Builds the Docker image.
  - `make interactive`: Launches a bash session inside the Docker container.
  - `make notebook`: Starts a Jupyter Notebook server.
  - `make flask`: Starts the Flask server on port `4000`.
  - `make db_create`: Creates the SQLite database `stocks.db`.
  - `make db_load`: Loads stock data into the database.
  - `make db_rm`: Deletes the `stocks.db` database.
  - `make db_clean`: Cleans, resets, and reloads the database.

### **requirements.txt**
- Lists all Python libraries and versions required for the project.

### **stock_app folder**
- Contains the core application.

#### **app.py**
- The main entry point for the Flask application, setting up and running the API server.

#### **api folder**
- Hosts all modules related to the API endpoints.
- Organized to support versioned API management.

---

## API Versions and Features

### **basic_stocks folder**
- Implements foundational routes for stock data operations:
  - `/api/v1/row_by_market_count`: Returns row counts grouped by market (NASDAQ, NYSE).
  - `/api/v1/unique_stock_count`: Returns the count of unique stock symbols.
  - `/api/v1/row_count`: Returns the total number of rows.

### **stock_price folder**
- Adds routes for price details and filtering:
  - `/api/v2/<price_type>/<symbol>`: Returns price information (Open, Close, High, Low) for a stock symbol.
  - `/api/v2/<year>`: Returns the count of stock records for a specific year.

### **accounts_management folder**
- Introduces account management:
  - `/api/v3/accounts`: Handles GET, POST, and DELETE for account data.
  - `/api/v3/stocks/<symbol>`: Returns stock holdings for a specific stock symbol.
  - `/api/v3/accounts/<acc_id>`: Returns stock holdings for a specific account ID.
  - `/api/v3/stocks`: Handles adding and deleting stock data.
  - `/api/v3/accounts/return/<account_id>`: Calculates the nominal return for a specific account.

### **backtesting folder**
- Adds backtesting functionality:
  - `/api/v4/back_test`: Handles POST requests for backtesting calculations, returning total returns and observations.

---

## Utility Folders

### **route_utils**
- Provides decorators and utility functions for API routes (e.g., authentication and logging).

### **data_utils**
- Contains utilities for data parsing and database interactions.

### **logger_utils**
- Centralized configuration for custom logging.

---

## Testing

### **Test folder**
- Contains all testing-related files.

#### **test.py**
- A Python file dedicated to running tests.

---

## Configuration Files

- **`pyproject.toml`**: Defines parameters for `ruff` lint checks.
- **`.pre-commit-config.yaml`**: Configures `ruff` pre-commit hooks for consistent code style.
