FROM python:3.10-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    ffmpeg git \
    && apt-get clean

# 安装 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建工作目录
WORKDIR /app

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
