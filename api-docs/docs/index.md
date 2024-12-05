<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Overview - Stock Market API</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', Arial, sans-serif;
            line-height: 1.6;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            color: #333;
        }

        .container {
            max-width: 900px;
            margin: 50px auto;
            padding: 30px;
            background-color: #ffffff;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
        }

        h1 {
            text-align: center;
            color: #222;
            font-weight: 700;
            margin-bottom: 30px;
            background: linear-gradient(to right, #6a11cb, #2575fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        h2 {
            color: #444;
            font-weight: 500;
            margin-top: 20px;
        }

        p {
            color: #555;
            margin-bottom: 20px;
            text-align: justify;
        }

        .image-container {
            text-align: center;
            margin: 30px 0;
        }

        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        footer {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background-color: #f4f4f9;
            color: #777;
            border-top: 1px solid #ddd;
        }

        footer p {
            margin: 0;
        }

        .highlight {
            font-weight: 500;
            color: #2575fc;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Stock Market Software Engineering Project</h1>

        <p>
            Welcome to the project overview for Group 2's <span class="highlight">Stock Market Software Engineering Project</span>. This initiative focused on building a robust data-serving API for stock market data from NASDAQ and NYSE spanning 2010-2020. The project comprises four progressive versions, each offering distinct functionality and utilizing technologies such as Flask, Docker, automated documentation, and thorough testing.
        </p>

        <h2>Version 1: Basic Stocks</h2>
        <p>
            This version provides essential API routes for delivering row counts, unique stock counts, and market-specific row counts (NYSE and NASDAQ) using data from the 2019 stock dataset.
        </p>

        <h2>Version 2: Stock Price</h2>
        <p>
            The /api/v2/ routes enable fetching stock price data by symbol and price type or retrieving the count of stock records for a specific year, ensuring input validation and returning JSON responses.
        </p>

        <h2>Version 3: Accounts Management</h2>
        <p>
            This version introduces comprehensive routes for managing accounts, stock data, and calculating returns. It supports CRUD operations, integrates authentication, and includes robust error handling.
        </p>

        <h2>Version 4: Backtesting</h2>
        <p>
            The /api/v4/back_test route allows users to perform backtesting calculations on stock data, providing total returns and observation counts based on user-defined parameters, complete with validation, authentication, and logging.
        </p>

        <div class="image-container">
            <img src="stock.jpg" alt="Stock Market Overview">
        </div>

        <footer>
            <p>&copy; 2024 Team API Docs. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
