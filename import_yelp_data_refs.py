#!/usr/bin/env python3

import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def update_batch(commands, bulk_url):
    """
    Sends a batch of commands to the database.
    """
    response = requests.post(
        bulk_url, data=json.dumps({"Commands": commands}), headers={"Content-Type": "application/json"}
    )

    if response.status_code != 201:
        print(f"Failed to insert data: {response.text}")


def process_references(query_url, session, batch_size, tuple, bulk_url, local_count, big_batch_size):
    counter = 0
    commands = []

    r = requests.get(
        f"{query_url}from%20{tuple[0]}%20limit%20{big_batch_size}%20offset%20{local_count}",
        headers={"Content-Type": "application/json"},
    )

    for result in r.json()["Results"]:
        for i in range(len(tuple[1])):
            original_col_name = tuple[1][i]
            original_collection = tuple[2][i]

            r2 = session.get(
                f"{query_url}from%20{original_collection}%20where%20{original_col_name}%20=%20'{result[original_col_name]}'",
            )

            # get the reference IDs
            for result2 in r2.json()["Results"]:
                # there should only be one result, if not, overwrite it - not our problem
                result[f"reference_{original_col_name}"] = result2["@metadata"]["@id"]

        commands.append(
            {
                "Id": result["@metadata"]["@id"],
                "Document": result,
                "Type": "PUT",
            }
        )

        if len(commands) % batch_size == 0:
            update_batch(commands, bulk_url)
            counter += batch_size
            print(f"Inserted {counter} records")
            commands = []

    if len(commands) > 0:
        update_batch(commands, bulk_url)
        counter += batch_size
        print(f"Inserted {counter} records")

    print(f"Processed a batch refs for {tuple[0]}.")


def main(database_url):

    # The format is: which collection to update, which fields should we reference
    # and which collection should we reference when looking for the fields,
    # the last parameter is a number of records in the collection to process
    references_list = [
        # ("yelp_academic_dataset_checkin", ["business_id"], ["yelp_academic_dataset_business"], 131_930),
        # ("yelp_academic_dataset_tip", ["business_id", "user_id"], ["yelp_academic_dataset_business", "yelp_academic_dataset_user"], 908_915),
        (
            "yelp_academic_dataset_review",
            ["business_id", "user_id"],
            ["yelp_academic_dataset_business", "yelp_academic_dataset_user"],
            6_990_280,
        ),
    ]

    batch_size = 1_000
    big_batch_size = 1_000_000
    query_url = f"{database_url}/databases/yelpdb/queries?query="
    bulk_url = f"{database_url}/databases/yelpdb/bulk_docs"

    # Create a session with retries to avoid connection errors
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for tuple in references_list:
        local_count = 0
        while local_count < tuple[3]:
            print(f"Processing refs for {tuple[0]}: {local_count} records processed.")
            process_references(query_url, session, batch_size, tuple, bulk_url, local_count, big_batch_size)
            local_count += big_batch_size

        process_references(query_url, session, batch_size, tuple, bulk_url, local_count, big_batch_size)


main("http://localhost:8080")
