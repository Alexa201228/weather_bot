FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# Add the Google Chrome repository
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Update the package list and install a specific version of Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable=114.0.5735.90

# Install unzip for extracting ChromeDriver
RUN apt-get install -yqq unzip

# Get the corresponding ChromeDriver version
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$(114)) && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port to avoid crashes
ENV DISPLAY=:99

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app/
CMD ["python3", "bot_app/bot_engine.py"]
