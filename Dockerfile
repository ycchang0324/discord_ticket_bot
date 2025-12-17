# 使用官方 Python 映像檔
FROM --platform=linux/amd64 python:3.10-slim

# 設定環境變數，避免安裝過程中的互動提示
ENV DEBIAN_FRONTEND=noninteractive

# 1. 安裝基礎依賴
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    --no-install-recommends

# 2. 加入 Google Chrome 儲存庫並下載金鑰
RUN curl -fSsL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# 3. 安裝 Chrome (移除掉可能導致錯誤的 libgconf-2-4)
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libnss3 \
    libxss1 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]