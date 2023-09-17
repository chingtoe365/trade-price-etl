FROM condaforge/mambaforge:4.14.0-0 as mambaforge
FROM selenium/standalone-chrome:116.0.5845.187

ARG CONDA_ENV_FILE=$CONDA_ENV_FILE
COPY ./$CONDA_ENV_FILE /environment.yml

# mamba command
COPY --from=mambaforge --chown=0:0 /opt /opt
RUN sudo chmod 777 --recursive /opt/conda
ENV PATH /opt/conda/bin:$PATH

RUN mamba update --yes -n base mamba \
    && conda config --set ssl_verify false \
    && mamba env create -n trade-price-etl -f /environment.yml \
    && mamba clean --all --yes

COPY ./src /app
COPY ./docker/scripts/start.sh /start.sh
RUN sudo chmod +x /start.sh
# set paths
ENV PYTHONPATH=/app
