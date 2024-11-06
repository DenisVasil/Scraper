# Base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget unzip curl && \
    apt-get install -y libnss3 libxss1 libappindicator3-1 fonts-liberation libgbm-dev xdg-utils && \
    apt-get clean

# Install Chrome browser
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY app.py /app/app.py
WORKDIR /app

# Expose port for Streamlit
EXPOSE 8501

# Run the app
CMD ["python", "app.py"]
