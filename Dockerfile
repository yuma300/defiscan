FROM python:3
USER root


RUN pip install requests
RUN pip install pandas
RUN pip install stellar-sdk
