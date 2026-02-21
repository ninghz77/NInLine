FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD gunicorn webapp:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 60
