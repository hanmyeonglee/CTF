FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir uploads

CMD ["python", "app.py"]