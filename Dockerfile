FROM python:3.11.5-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY data/raw_data ./data/raw_data
COPY app.py .

ENV PYTHONUNBUFFERED=1

ENV FLASK_APP=app.py

EXPOSE 4000

CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]
