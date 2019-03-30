FROM python:3.6.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /opt/backend
ADD . /opt/backend
WORKDIR /opt/backend

RUN pip install -U pip
RUN pip install uwsgi
RUN pip install -r requirements.txt
