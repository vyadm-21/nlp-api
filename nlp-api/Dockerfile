FROM python:3

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./

RUN apt-get update -y && apt-get install default-jre -y
RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app