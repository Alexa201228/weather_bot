FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    python3 python3-pip

# Gecko Driver
ENV GECKODRIVER_VERSION 0.32.0
RUN wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && mv /opt/geckodriver /opt/geckodriver-$GECKODRIVER_VERSION \
  && chmod 755 /opt/geckodriver-$GECKODRIVER_VERSION \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/bin/geckodriver \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/bin/wires

RUN sh -c 'echo "APT::Default-Release "stable";" >> /etc/apt/apt.conf'
RUN sh -c 'echo "deb http://ftp.hr.debian.org/debian sid main contrib non-free" >> /etc/apt/sources.list'
RUN apt-get update -y && apt-get install -yt sid firefox

ENV DISPLAY=:99

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app/
CMD ["python3", "bot_app/bot_engine.py"]
