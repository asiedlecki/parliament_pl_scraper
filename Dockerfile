# syntax=docker/dockerfile:1
# FROM python:3.8
ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

LABEL author="Artur Siedlecki"

RUN pip install pipenv

COPY . /

RUN pip install requests urllib3 beautifulsoup4
RUN pip install selenium pymongo