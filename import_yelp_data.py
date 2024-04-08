#!/usr/bin/env python3

import json
import requests


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

        json_request["Commands"].append({"Id": collection_name + "/" + str(id), "Document": data, "Type": "PUT"})

    # Insert the data into the database
    response = requests.post(db_url_full, data=json.dumps(json_request), headers={"Content-Type": "application/json"})

    # Check if the request was successful
    if response.status_code != 201:
        print(f"Failed to insert data: {response.text}")


def process_file(file, id_type, db_url):
    """
    Goes through the file and inserts the data into the database.
    """

    # Read the file (line by line, it is too big to read at once)
    counter = 0
    current_batch = []
    batch_size = 1_000

    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            counter += 1
            data = json.loads(line)
            if id_type is not None:
                current_batch.append((data, data[id_type]))
            else:
                current_batch.append((data, counter))
            if counter % batch_size == 0:
                insert_batch(current_batch, db_url, file.split(".")[0])
                current_batch = []

    if len(current_batch) > 0:
        insert_batch(current_batch, db_url, file.split(".")[0])

    print(f"Finished processing {file}")


def filter_users(files):
    """
    Filters the users that are relevant for the tip data.
    """
    used_users = set()

    print("Filtering users")
    with open("yelp_academic_dataset_tip.json", "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            used_users.add(data["user_id"])

    with open("yelp_academic_dataset_user.json", "r", encoding="utf-8") as f:
        with open("yelp_academic_dataset_user_filtered.json", "w", encoding="utf-8") as f2:
            for line in f:
                data = json.loads(line)
                if data["user_id"] in used_users:
                    f2.write(json.dumps(data) + "\n")

    files.remove(("yelp_academic_dataset_user.json", "user_id"))
    files.append(("yelp_academic_dataset_user_filtered.json", "user_id"))


def add_references(files):
    """
    Adds references to the checkin and tip data.
    """

    print("Adding references to checkin")
    with open("yelp_academic_dataset_checkin.json", "r", encoding="utf-8") as f:
        with open("yelp_academic_dataset_checkin_refs.json", "w", encoding="utf-8") as f2:
            for line in f:
                data = json.loads(line)
                data["reference_business_id"] = f"yelp_academic_dataset_business/" + data["business_id"]
                f2.write(json.dumps(data) + "\n")

    files.remove(("yelp_academic_dataset_checkin.json", None))
    files.append(("yelp_academic_dataset_checkin_refs.json", None))

    print("Adding references to tip")
    with open("yelp_academic_dataset_tip.json", "r", encoding="utf-8") as f:
        with open("yelp_academic_dataset_tip_refs.json", "w", encoding="utf-8") as f2:
            for line in f:
                data = json.loads(line)
                data["reference_business_id"] = f"yelp_academic_dataset_business/" + data["business_id"]
                data["reference_user_id"] = f"yelp_academic_dataset_user_filtered/" + data["user_id"]
                f2.write(json.dumps(data) + "\n")

    files.remove(("yelp_academic_dataset_tip.json", None))
    files.append(("yelp_academic_dataset_tip_refs.json", None))


def main(db_url, preprocess_raw_data=True):
    """
    The entry point of the script.
    Assumes that:
        - files yelp_*.json are in the same directory as this script
        - the database is running and there exists a database called yelpdb
    """
    files_and_ids = [
        ("yelp_academic_dataset_business.json", "business_id"),
        ("yelp_academic_dataset_checkin.json", None),
        ("yelp_academic_dataset_tip.json", None),
        ("yelp_academic_dataset_user.json", "user_id"),
    ]

    if preprocess_raw_data:
        filter_users(files_and_ids)
        add_references(files_and_ids)

    for tuple in files_and_ids:
        process_file(tuple[0], tuple[1], db_url)


main("http://localhost:8080", True)
