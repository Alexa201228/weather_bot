FROM joyzoursky/python-chromedriver:3.8
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app/
CMD ["python3", "bot_engine.py"]
