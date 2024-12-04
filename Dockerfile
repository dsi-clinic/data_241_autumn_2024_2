# Use Python 3.11.5 as the base image
FROM python:3.11.5-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .

# Install Python dependencies without caching to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite (required for database operations)
RUN apt-get update 
RUN apt-get install -y --no-install-recommends sqlite3

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app

# Expose port 4000 for Flask
EXPOSE 4000

# Default command to run the Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]