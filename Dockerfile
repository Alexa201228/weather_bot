FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl unzip && \
    apt-get clean

# Download and install Google Chrome
RUN wget -q --continue -P /tmp https://storage.googleapis.com/chrome-for-testing-public/GoogleChrome-stable_current_amd64.deb && \
    dpkg -i /tmp/GoogleChrome-stable_current_amd64.deb || apt-get -y install -f && \
    rm /tmp/GoogleChrome-stable_current_amd64.deb

# Get the installed version of Google Chrome
RUN CHROME_VERSION=$(google-chrome --product-version | cut -d '.' -f 1-3) && \
    echo "Chrome Version: $CHROME_VERSION"

# Download and install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -s "https://storage.googleapis.com/chrome-for-testing-public/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -q --continue -P /tmp "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver-linux64.zip

# Set display port to avoid crashes
ENV DISPLAY=:99

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app/
CMD ["python3", "bot_app/bot_engine.py"]
