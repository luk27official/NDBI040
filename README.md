# NDBI040

A repository for the NDBI040 subject.

## Docker with database

1. `docker-compose build`
2. `docker-compose up`
3. Open `localhost:8080` in your browser.

The RavenDB studio is available at `localhost:8080` (bonus: the frontend at `localhost:3001`).

## Importing the Yelp dataset

To import the Yelp dataset, do the following:
1. Download it from [here](https://www.kaggle.com/datasets/yelp-dataset/yelp-dataset).
2. Extract it to the root folder.
3. Ensure that the database is running.
4. Run `python import_yelp_data.py` to import the data.

## Running the queries for Yelp

1. Python: Run `python query_executor.py`.

## BONUS: Frontend local development

1. `npm i`
2. `npm run dev`

The frontend is then available at `localhost:3000`.
