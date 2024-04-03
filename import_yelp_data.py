#!/usr/bin/env python3

import json
import requests


def insert_data(data, db_url, id, collection_name):
    """
    Inserts the data into the database.
    Not used - too slow for large datasets.
    """

    # <server URL>/databases/<database name>/docs?id=<document ID>/
    db_url_full = db_url + "/databases/yelpdb/docs?id=" + collection_name + "_" + str(id) + "/"

    data["@metadata"] = {}
    data["@metadata"]["@collection"] = collection_name

    # Insert the data into the database
    response = requests.put(db_url_full, data=json.dumps(data))

    # Check if the request was successful
    if response.status_code != 201:
        print(f"Failed to insert data: {response.text}")


def insert_batch(batch, db_url, collection_name):
    """
    Inserts the data into the database in a batch.
    """
    # https://ravendb.net/docs/article-page/6.0/csharp/client-api/rest-api/document-commands/batch-commands
    # <server URL>/databases/<database name>/bulk_docs
    db_url_full = db_url + "/databases/yelpdb/bulk_docs"

    json_request = {}
    json_request["Commands"] = []

    for data, id in batch:
        data["@metadata"] = {}
        data["@metadata"]["@collection"] = collection_name

        json_request["Commands"].append({"Id": collection_name + "_" + str(id), "Document": data, "Type": "PUT"})

    # Insert the data into the database
    response = requests.post(db_url_full, data=json.dumps(json_request), headers={"Content-Type": "application/json"})

    # Check if the request was successful
    if response.status_code != 201:
        print(f"Failed to insert data: {response.text}")


def process_file(file, db_url):
    """
    Goes through the file and inserts the data into the database.
    """

    # Read the file (line by line, it is too big to read at once)
    counter = 0
    current_batch = []
    batch_size = 1000

    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            counter += 1
            data = json.loads(line)
            current_batch.append((data, counter))
            if counter % batch_size == 0:
                insert_batch(current_batch, db_url, file.split(".")[0])
                current_batch = []

    if len(current_batch) > 0:
        insert_batch(current_batch, db_url, file.split(".")[0])

    print(f"Finished processing {file}")


def main(db_url):
    """
    The entry point of the script.
    Assumes that:
        - files yelp_*.json are in the same directory as this script
        - the database is running and there exists a database called yelpdb
    """
    files = [
        # "yelp_test.json",
        "yelp_academic_dataset_business.json",
        "yelp_academic_dataset_checkin.json",
        "yelp_academic_dataset_review.json",
        "yelp_academic_dataset_tip.json",
        "yelp_academic_dataset_user.json",
    ]

    for file in files:
        process_file(file, db_url)


main("http://localhost:8080")
