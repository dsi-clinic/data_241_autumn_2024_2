# data_241_autumn_2024_2

This repository contains a basic dockerfile that will run a jupyter notebook instance. To build the docker image, please type in:

docker build . -t data241

Note that the image name in the above command is drw

To run the image type in the following:

docker run -p 8888:8888 -v ${PWD}:/tmp data241

as you can see we are running the data241 image.

People

Anuj Agarwal - 4th-year Undergraduate Data Science major

Disha Mohta - 4th-year Undergraduate Economics and Data Science major

Ishani Raj - 3rd-year Undergraduate exchange student

Ken Law - 4th-year Undergraduate MENG major

Folders and Files

Util folder - Our code is in this folder

Data folder - All our data is in this folder

DockerFile - Has instructions to run code and set up proper environment conditions 

requirements.txt - All python/library versions for the project

app.py - Serves as the entry point for the Flask application, responsible for setting up and running the API server. This file is kept minimal and only manages the high-level application setup. 

Application Initialization: create_app() function initializes the Flask app, registers API routes, and configures the server.

Route Registration: Routes from different modules are registered here, allowing for modular organization of API versions and endpoints.

Server Configuration: The application is configured to run on host='0.0.0.0' and port=5000 by default for external access within Docker.

test.py - lightweight testing script to validate the functionality of the API endpoints. It helps confirm that the Flask API server is correctly processing requests and handling authorization. 

Key features include:

API Key Authentication: Ensures that requests include a valid DATA-241-API-KEY header, as required by the API. Incorrect or missing keys should trigger a 401 Unauthorized response.

Endpoint Testing: Includes functions to send GET requests to various endpoints (e.g., /api/v2/{YEAR}, /api/v2/open/{SYMBOL}), validating responses, and printing status codes and response content.

Error Handling: Provides exception handling for request errors, making it easier to diagnose issues with endpoint communication.

Makefile: Simplifies and automates common tasks, enabling smooth development and testing workflows. Each command encapsulates a different aspect of the project setup and execution, making it easier to build, test, and run the application within a Docker environment. 

