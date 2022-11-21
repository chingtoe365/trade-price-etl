FROM conda/miniconda3

COPY ./${CONDA_ENV_FILE}.yml /environment.yml

RUN echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf \
    && echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf \
    && apt-get update && apt-get -y upgrade && apt-get -y install git libxrender1 libxext6 build-essential  \
    && conda update -n base -c defaults conda \
    && conda config --set ssl_verify false \
    && conda env create -n etl -f /environment.yml \
    && conda clean --all --yes

ARG USER_NAME=upwhirlpilot
ARG USER_ID=8888
ARG GROUP_NAME=billion
ARG GROUP_ID=888

RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ]; then \
    if [ $(id -u ${USER_NAME} > /dev/null 2>&1; echo $?) -ne 1 ]; then userdel -f ${USER_NAME}; fi &&\
    if getent group ${GROUP_NAME} ; then groupdel ${GROUP_NAME}; fi &&\
    groupadd -g ${GROUP_ID} ${GROUP_NAME} &&\
    useradd -l -u ${USER_ID} -g ${GROUP_NAME} ${USER_NAME} &&\
    install -d -m 0755 -o ${USER_NAME} -g ${GROUP_NAME} /home/${USER_NAME}\
;fi

# set paths
ENV PYTHONPATH=/app
COPY --chown=$USER_NAME:$GROUP_NAME ./src /app