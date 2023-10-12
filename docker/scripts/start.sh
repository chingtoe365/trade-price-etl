#!/usr/bin/env bash

# Bash script to start ETl pipeline

source activate trade-price-etl

#conda list | grep pandas
#conda list | grep numpy

if [[ -n $1 ]];
then
  echo ">> Developer mode"
  watchfiles "python -m trade_price_etl" /app
else
  echo ">> Production mode"
  python -m trade_price_etl
fi