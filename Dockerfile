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

# 切換到 root 權限進行安裝
USER root

# 安裝中文字型與字型管理工具
RUN apt-get update && apt-get install -y \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 更新字型快取，確保系統抓到新字型
RUN fc-cache -fv

# 設定語系環境變數為 UTF-8
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# 設定工作目錄
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]