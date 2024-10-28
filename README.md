# data_241_autumn_2024_2

# Repository Setup Guide

To set up and run this repository, execute the following commands in your terminal:

1. make build - This should build the image from the dockerfile in your repo

2. make interactive - This should start an interactive bash session with the current working directory mounted to /app/src

3. make notebook - This should start a notebook server with the current working directory mounted /app/src and ports properly set up so that the notebook can be accessed.

4. make flask - This should start the flask server, making sure to expose port 4000 so that we can ping the API from outside the container.

# People

Anuj Agarwal - 4th-year Undergraduate Data Science major

Disha Mohta - 4th-year Undergraduate Economics and Data Science major

Ishani Raj - 3rd-year Undergraduate exchange student

Ken Law - 4th-year Undergraduate MENG major

# Folders and Files

data folder - All our data is in this folder. It contains a subfolder called raw data which contains NASDAQ_2019.zip and NYSE_2019.zip.

util folder - some extra python files. Currently empty as there are no extraneous files.

DockerFile - The Dockerfile provides a blueprint for building a consistent, isolated environment in which the application can run. It includes the following configurations:

Base Image: Specifies a base Docker image, such as python:3.x, ensuring the correct Python version is used.

Dependencies: Installs all required Python libraries as listed in requirements.txt, ensuring compatibility and consistency.

Directory Setup: Sets up the /app/src directory where the application code is mounted, aligning with the Makefile commands for interactive sessions and server startups.

Entrypoint: Configures default commands or environment variables if needed for the container to run the application, typically set up for make flask or make notebook.

Makefile -  The Makefile in this project automates common setup and execution tasks, providing an easy-to-use interface to streamline the development workflow. Below are the main commands included in the Makefile:

make build: Builds the Docker image for the application using the Dockerfile in the repository. This prepares a container environment with all dependencies installed.

make interactive: Launches an interactive bash session inside the Docker container, mounting the current working directory to /app/src. This allows for direct interaction with the container environment, making it useful for debugging and development.

make notebook: Starts a Jupyter Notebook server with the current working directory mounted at /app/src and properly sets up port forwarding, allowing access to the notebook from outside the container.

make flask: Starts the Flask server in the Docker container, exposing port 4000 to make the API accessible from outside the container.

requirements.txt - All python/library versions for the project.

stock_app - the entire app as a folder

app.py - The app.py file serves as the main entry point for the Flask application, responsible for setting up and running the API server. This file initializes the application and organizes the routing, ensuring a modular and organized structure for handling API requests.

api folder - The api/ folder contains all modules related to the API endpoints of the Flask application. This folder is organized to support modular routing and versioned API management, ensuring that different versions of the API can coexist and evolve independently.

v1 folder - The v1/ directory holds the first version of the API endpoints. This version typically includes foundational routes and functionality, often setting the baseline behavior for the API.

v2 folder - The v2/ directory hosts the second version of the API, incorporating additional features, improvements, or refined endpoint behaviors.

route_utils - The route_utils/ directory provides utility functions and decorators that support the API routes across versions.

decorators.py -  Custom decorators for functions such as API key validation, ensuring that requests meet authentication requirements.

Test - folder containing files for testing the code.

test.py - dedicated python file to run and test the code.

