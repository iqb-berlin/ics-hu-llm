FROM python:3.11

COPY ics /app/ics
COPY lib /app/lib

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install pydevd-pycharm==243.26053.29
