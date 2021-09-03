# syntax=docker/dockerfile:1
FROM python:3.8
RUN pip install pipenv
EXPOSE 8501
# COPY ./requirements.txt /requirements.txt
WORKDIR /
COPY . /
RUN pipenv install --system --deploy