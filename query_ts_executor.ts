import { DocumentStore, IDocumentSession, SessionOptions } from "ravendb";

async function query313(session: IDocumentSession) {
    const start = new Date().getTime();
    const results = await session.query({ collection: "yelp_academic_dataset_business" })
        .whereRegex("name", "^A").all();
    const end = new Date().getTime();

    return {
        query: "3.1.3",
        time: (end - start),
        results: results.length
    };
}

async function query314(session: IDocumentSession) {
    const start = new Date().getTime();
    const results = await session.query({ collection: "yelp_academic_dataset_business" })
        .whereBetween("stars", 3, 4).all();
    const end = new Date().getTime();

    return {
        query: "3.1.4",
        time: (end - start),
        results: results.length
    };
}

async function query321(session: IDocumentSession) {
    const start = new Date().getTime();
    const results = await session.query({ collection: "yelp_academic_dataset_user_filtered" })
        .groupBy("review_count").selectKey().selectCount().all();
    const end = new Date().getTime();

    return {
        query: "3.2.1",
        time: (end - start),
        results: results.length
    };
}

// queries 3.3.2 - 3.3.3 have no equivalent in the Node.js API (just raw queries)

async function query342(session: IDocumentSession) {
    const start = new Date().getTime();
    const results = await session.query({ collection: "yelp_academic_dataset_tip_refs" })
        .whereRegex("text", "chicken")
        .intersect()
        .whereEquals("compliment_count", 0)
        .all();
    const end = new Date().getTime();

    return {
        query: "3.4.2",
        time: (end - start),
        results: results.length
    };
}

async function query352(session: IDocumentSession) {
    const start = new Date().getTime();
    const results = await session.query({ collection: "yelp_academic_dataset_business" })
        .orderBy("latitude").all();
    const end = new Date().getTime();

    return {
        query: "3.5.2",
        time: (end - start),
        results: results.length
    };
}

async function query361(session: IDocumentSession) {
    const start = new Date().getTime();
    const results = await session.query({ collection: "yelp_academic_dataset_business" })
        .selectFields("state").distinct().all();
    const end = new Date().getTime();

    return {
        query: "3.6.1",
        time: (end - start),
        results: results.length
    };
}

async function query37(session: IDocumentSession) {
    // assumes the index "count-tips-by-business" is created
    const start = new Date().getTime();
    const results = await session.query({ indexName: "count-tips-by-business" }).all();
    const end = new Date().getTime();

    return {
        query: "3.7",
        time: (end - start),
        results: results.length
    };
}

async function main(serverUrl: string, caching: boolean) {
    const databaseName = 'yelpdb';

    const store = new DocumentStore([serverUrl], databaseName);
    store.initialize();

    try {
        const sessionOptions: SessionOptions = {
            noCaching: !caching
        };

        // run queries
        const run_count = 20 + 2; // 20 runs + 2 to eliminate max and min times

        const queries = [
            query313, query314, query321, query342,
            query352, query361, query37
        ];

        const finalResults = new Map<string, number[]>();

        for (const query of queries) {
            for (let i = 0; i < run_count; i++) {
                const session = store.openSession(sessionOptions);
                const result = await query(session);
                console.log(`Query ${result.query} took ${result.time} ms, found ${result.results} results.`);
                if (!finalResults.has(result.query)) {
                    finalResults.set(result.query, []);
                }
                finalResults.get(result.query)!.push(result.time);
            }
        }

        // group finalResults by query name and calculate average time
        const avgResults = new Map<string, number>();
        // remove max and min times
        for (const [query, times] of Array.from(finalResults.entries())) {
            const max = Math.max(...times);
            const min = Math.min(...times);
            const filteredTimes = times.filter(t => t !== max && t !== min);
            finalResults.set(query, filteredTimes);
        }

        for (const [query, times] of Array.from(finalResults.entries())) {
            const avg = times.reduce((acc, val) => acc + val, 0) / times.length;
            avgResults.set(query, avg);
        }

        console.table(Array.from(avgResults.entries()));

    } finally {
        store.dispose();
    }
};

main("http://localhost:8080", true);