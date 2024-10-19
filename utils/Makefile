IMAGE_NAME=flask_notebook_app

# Define phony targets
.PHONY=build notebook interactive flask

# Build the docker image
build:
	docker build . -t $(IMAGE_NAME)

# Start an interactive bash session with current directory mounted
interactive: build
	docker run -it \
	-v $(shell pwd):/app/src \
	$(IMAGE_NAME) /bin/bash

# Start an interactive Jupyter notebook with current directory mounted
notebook: build
	docker run -it -p 8888:8888 \
	-v $(shell pwd):/app/src \
	$(IMAGE_NAME) \
	jupyter notebook --allow-root --no-browser \
	--port 8888 --ip=0.0.0.0

# Start the Flask server
flask: build
    docker run -p 4000:5000 \
    -e FLASK_APP=/app/src/app.py \
    -e FLASK_DEBUG=1 \
    -e FLASK_ENV=development \
	-v $(shell pwd):/app/src \
	$(IMAGE_NAME) \

