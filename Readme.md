## NBA players clustering
## Final project - AGH Data Science/Big Data postgraduates study

### Data engineering ->
    Apache Airflow -> orchiestration
    Pyspak -> Data processing, ingestion, transformations
    Database -> Postgresql
    Web Scraping -> Selenium, BeautifulSoup, AioHttp, Asyncio
    Services created in docker containers (Docker, docker-compose)

### Data analysis
    Python, Sklearn, Pyspark, Pandas, Seaborn, Matplotlib

### Guide

1. Install docker and docker-compose
2. Clone project from repository and go to Project root directory
3. Run command docker-compose up -build
4. After creation of whole environment:
    - localhost:8080 - airflow
    - localhost:8888 - jupyter
    - localhost:7071 - spark
5. Go to airflow and trigger dags:
    - deploy_connection
    - spark_load_to_postgres
Now data are flowing to postgresql database

If you want to query data you can go to docker container bash -
command: docker exec -it <container_id> bash
to get container id type docker ps command

6. Go to jupyter notebook and run all cells if you want



