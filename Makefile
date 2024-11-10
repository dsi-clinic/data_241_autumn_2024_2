# Define the image name and handle API key from the environment
IMAGE_NAME=flask_notebook_app
DATA_241_API_KEY ?= disha
DB_PATH=/app/src/data/stocks.db # CHECK

# Define phony targets to avoid conflicts with files named build, notebook, etc.
.PHONY: build interactive notebook flask \
	db_clean db_create db_load db_rm 

COMMON_DOCKER_FLAGS= \
	-v $(shell pwd):/app/src \
	-e FLASK_APP=/app/src/app.py \
	-e FLASK_DEBUG=1 \
	-e FLASK_ENV=development \
	-e DB_PATH=$(DB_PATH) \
	-e DATA_DIR=/app/src/data \

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

db_create: build
	docker run $(COMMON_DOCKER_FLAGS) $(IMAGE_NAME) \
		python /app/src/app/stock_app/api/data_utils/db_manage.py db_create

db_load: build
	docker run $(COMMON_DOCKER_FLAGS) $(IMAGE_NAME) \
		python /app/src/app/stock_app/api/data_utils/db_manage.py db_load

db_rm: build
	docker run $(COMMON_DOCKER_FLAGS) $(IMAGE_NAME) \
		python /app/src/app/stock_app/api/data_utils/db_manage.py db_rm

db_clean: build
	docker run $(COMMON_DOCKER_FLAGS) $(IMAGE_NAME) \
		python /app/src/app/stock_app/api/data_utils/db_manage.py db_clean
