# Define the image name and handle API key from the environment
IMAGE_NAME=flask_notebook_app
DATA_241_API_KEY ?= disha

# Define phony targets to avoid conflicts with files named build, notebook, etc.
.PHONY: build interactive notebook flask

# Build the Docker image
build:
	docker build . -t $(IMAGE_NAME)

# Start an interactive bash session with the current directory mounted
interactive: build
	docker run -it \
		-v $(shell pwd):/app/src \
		-e DATA_241_API_KEY=$(DATA_241_API_KEY) \
		$(IMAGE_NAME) /bin/bash

# Start an interactive Jupyter notebook with the current directory mounted
notebook: build
	docker run -it -p 8888:8888 \
		-v $(shell pwd):/app/src \
		$(IMAGE_NAME) \
		jupyter notebook --allow-root --no-browser \
		--port 8888 --ip=0.0.0.0

# Start the Flask server on port 4000
flask: build
	docker run -p 4000:4000 \
		-e FLASK_APP=/app/src/app.py \
		-e FLASK_DEBUG=1 \
		-e FLASK_ENV=development \
		-e DATA_241_API_KEY=$(DATA_241_API_KEY) \
		-v $(shell pwd):/app/src \
		$(IMAGE_NAME)
