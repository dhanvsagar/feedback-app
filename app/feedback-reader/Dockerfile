FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
        gcc \
        libpq-dev \
        python3-dev \
        && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY sentiment_analyzer.py .
COPY asana_client.py .

CMD ["python", "main.py"]