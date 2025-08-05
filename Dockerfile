FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg git \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
