# trade-price-etl
ETL tool to obtain trade data publicly 

### To Run the pipeline with docker
> cd docker
> 
> docker-compose build
> 
> docker-compose up
> 
This will run the pipeline to scrape crypto currrencies

### To run pipeline with python CLI
> conda env create -f environment.yml
> 
> source activate trade-price-etl
> 
> export PYTHONPATH=`pwd`/src
> 
> python -m trade_price_etl