FROM python:3
USER root

RUN pip install web3
RUN pip install eth-event
