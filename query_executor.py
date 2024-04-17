#!/usr/bin/env python3
import requests


def execute_query(query, db_url):
    """
    Executes the query against the database.
    """

    query_url = db_url + "/databases/yelpdb/queries?query=" + query.replace(" ", "%20")

    r = requests.get(
        f"{query_url}",
        headers={"Content-Type": "application/json"},
    )

    if r.status_code != 200:
        print(f"Failed to execute query: {r.text}")
        return -1

    response = r.json()

    # we are interested in the duration of the query, but you can also print the response to see the results
    return response["DurationInMs"]


def log_durations(results, run_count, file_name="results.csv"):
    """
    Logs the results to a file.
    """

    with open(file_name, "w") as f:
        f.write("query_num,")
        for i in range(1, run_count + 1 - 2):  # to eliminate max and min
            f.write(f"run_{i},")
        f.write("average\n")

        for key, value in results.items():
            value.remove(max(value))
            value.remove(min(value))

            f.write(f"{key},")
            for i in range(len(value)):
                f.write(f"{value[i]},")
            average = sum(value) / len(value)
            f.write(f"{average}\n")

    print(f"Results logged to {file_name}")


def main(db_url):
    """
    The entry point of the script.
    Assumes that the database is running and there exists a database called yelpdb.
    """

    queries = [
        ("3.1.3", 'from "yelp_academic_dataset_business" where search("name", "A*")'),
        ("3.1.4", 'from "yelp_academic_dataset_business" where stars < 5 and stars > 2'),
        (
            "3.2.1",
            'from "yelp_academic_dataset_user_filtered" group by "review_count" select key() as "key", count() as "Count"',
        ),
        (
            "3.3.2",
            'from "yelp_academic_dataset_tip_refs" as t load t.reference_user_id as u select { user: u.name text: t.text } limit 100000',
        ),
        (
            "3.3.3",
            'from "yelp_academic_dataset_tip_refs" as t load t.reference_user_id as u, t.reference_business_id as b select { user: u.name text: t.text business_id: b.business_id } limit 100000',
        ),
        (
            "3.4.2",
            'from "yelp_academic_dataset_tip_refs" where intersect(search("text", "*chicken*"), compliment_count == 0)',
        ),
        ("3.5.2", 'from "yelp_academic_dataset_business" order by latitude asc'),
        ("3.6.1", 'from "yelp_academic_dataset_business" select distinct state'),
        ("3.7", 'from index "count-tips-by-business"'),  # notice that the index needs to be created first
    ]

    results = {}

    run_count = 20 + 2  # to eliminate max and min

    for query in queries:
        for i in range(run_count):
            duration = execute_query(query[1], db_url)
            if duration == -1:
                continue

            if query[0] not in results:
                results[query[0]] = []

            results[query[0]].append(duration)
            print(f"Executed query {query[0]} in {duration} ms")

    log_durations(results, run_count)


main("http://localhost:8080")
