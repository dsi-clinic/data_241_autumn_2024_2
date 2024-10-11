FROM python:3.11.5-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY utils/eda_2019.py .
COPY data/raw_data ./data/raw_data

CMD ["python", "eda_2019.py"]