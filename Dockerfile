FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN playwright install
RUN playwright install-deps
COPY . /app/
CMD ["python3", "bot_app/bot_engine.py"]
