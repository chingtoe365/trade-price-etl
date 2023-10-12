FROM --platform=linux/amd64 condaforge/mambaforge:4.14.0-0 as mambaforge
FROM --platform=linux/amd64 selenium/standalone-chrome:116.0.5845.187

# setup proxies if needed
ARG HTTP_PROXY=$HTTP_PROXY
ARG HTTPS_PROXY=$HTTPS_PROXY
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY

# conda command
COPY --from=mambaforge --chown=0:0 /opt /opt
RUN sudo chmod 777 --recursive /opt/conda
ENV PATH /opt/conda/bin:$PATH

ARG CONDA_ENV_FILE=$CONDA_ENV_FILE
COPY ./$CONDA_ENV_FILE environment.yml
COPY ./pyproject.toml pyproject.toml
COPY ./poetry.lock poetry.lock
COPY ./README.md README.md

RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.2.2 python3 -

ENV PATH=$HOME/.local/bin:$PATH

RUN conda env create -f ./environment.yml
SHELL ["/bin/bash", "-c"]
RUN source activate trade-price-etl \
    && poetry install -vv --no-root

COPY ./src /app
#COPY ./docker/.env /app/trade_price_etl/.env
COPY ./docker/scripts/start.sh /start.sh
RUN sudo chmod +x /start.sh

WORKDIR /app

# set paths
ENV PYTHONPATH=/app
