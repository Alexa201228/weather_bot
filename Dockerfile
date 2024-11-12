FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# Update package lists and install Google Chrome
RUN apt-get -y update && apt-get install -y google-chrome-stable

# Install unzip utility for extracting ChromeDriver
RUN apt-get install -yqq unzip

# Get the version of Google Chrome installed
RUN CHROME_VERSION=$(google-chrome --version | sed 's/.* \([0-9]*\.[0-9]*\.[0-9]*\).*/\1/') && \
    CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set display port to avoid crash (needed for headless mode)
ENV DISPLAY=:99

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app/
CMD ["python3", "bot_app/bot_engine.py"]
