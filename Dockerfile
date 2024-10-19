FROM python:3.11.5-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY utils/eda_2019.py .
COPY data/raw_data ./data/raw_data

# Below allows for more consistent printing
ENV PYTHONUNBUFFERED=1

CMD ["python", "eda_2019.py", "flask", "run", "--host=0.0.0.0"]