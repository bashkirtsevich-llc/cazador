FROM python:3.7.0-alpine

MAINTAINER Bashkirtsev D.A. <bashkirtsevich@gmail.com>

WORKDIR /app

EXPOSE 22

COPY . .

RUN pip install -r requirements

CMD [ "python", "app.py" ]