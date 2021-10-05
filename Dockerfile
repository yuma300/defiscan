FROM python:3
USER root


RUN pip install requests
RUN pip install pandas
RUN pip install web3
RUN pip install eth-event
RUN pip install etherscan-python
RUN pip install git+https://github.com/ca3-caaip/caaj_evm.git
