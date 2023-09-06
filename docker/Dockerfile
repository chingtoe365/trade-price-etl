FROM condaforge/mambaforge:4.14.0-0

ARG CONDA_ENV_FILE=$CONDA_ENV_FILE
COPY ./$CONDA_ENV_FILE /environment.yml

# Set up Chromedriver Environment variables
# ENV CHROMEDRIVER_VERSION 107.0.5304.62
# ENV CHROMEDRIVER_VERSION 114.0.5735.90
# ENV CHROME_VERSION 107.0.5304.106
# ENV CHROMEDRIVER_VERSION 116.0.5845.140
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR

# We need wget to set up the PPA and xvfb to have a virtual screen and unzip to install the Chromedriver
RUN echo "Acquire::http::No-Cache false;" >> /etc/apt/apt.conf \
    && echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf \
    && apt-get update && apt-get -y upgrade \
    && apt-get -y install git libxrender1 libxext6 build-essential wget xvfb unzip

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    # Update the package list and install chrome
    && apt-get update -y \
#     && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y google-chrome-stable=$CHROME_VERSION
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y google-chrome-stable

# Download and install Chromedriver
# RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" \
RUN wget -q --continue -P $CHROMEDRIVER_DIR "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip" \
    && unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

RUN mamba update --yes -n base mamba \
    && conda config --set ssl_verify false \
    && mamba env create -n trade-price-etl -f /environment.yml \
    && mamba clean --all --yes

# # install chrome & chromedriver
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm \
#     && yum localinstall google-chrome-stable_current_x86_64.rpm

# RUN echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf \
#     && echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf \
#     && apt-get update && apt-get -y upgrade && apt-get -y install git libxrender1 libxext6 build-essential  \
#     && conda update -n base -c defaults conda \
#     && conda config --set ssl_verify false \
#     && conda env create -n etl -f /environment.yml \
#     && conda clean --all --yes

RUN apt-get -y install libgconf-2-4

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


COPY --chown=$USER_ID:$GROUP_ID ./src /app
COPY --chown=$USER_ID:$GROUP_ID ./docker/scripts/start.sh /start.sh
RUN chmod +x /start.sh
# set paths
ENV PYTHONPATH=/app
# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR/chromedriver-linux64:$PATH
