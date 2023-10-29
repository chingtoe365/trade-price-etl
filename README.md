# trade-price-etl
ETL tool to obtain trade data publicly

### To Run the pipeline with docker
> cd docker
>
> docker-compose build
>
> docker-compose -f docker-compose.development.yml up
>
This will run the pipeline to scrape crypto currrencies

### What it does

1. Monitor the prices changes in the live website
2. Publish a message to mosquitto message broker via MQTT protocal
3. The message broker has 2 applications
    1. MQTT listen on 1883
    2. Websocket listen on 8080

4. Background Application can subscribe on tcp://localhost:1883 to receive notification
5. Broswer application can subscribe on ws://localhost:8080 to receive notification
    1. Test cliet: https://mitsuruog.github.io/what-mqtt/
    2. Type `ws://localhost:8080` to Address
    3. Subscript one topic: e.g. Solana

### To run pipeline with python CLI
> conda env create -f environment.yml
>
> source activate trade-price-etl
>
> export PYTHONPATH=`pwd`/src
>
> python -m trade_price_etl
