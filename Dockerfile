# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Install system dependencies for Chrome
RUN apt-get update && \
    apt-get install -y wget unzip curl && \
    apt-get install -y libnss3 libxss1 libappindicator1 libindicator7 libgbm-dev && \
    apt-get install -y fonts-liberation libappindicator3-1 xdg-utils && \
    apt-get clean

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && \
    rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver

# Set display port to avoid errors with headless Chrome
ENV DISPLAY=:99

# Set the working directory
WORKDIR /app

# Copy the local project files to the Docker container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Streamlit
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
