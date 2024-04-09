**Perform a static analysis of the supported data models and query languages. Specifically, for each supported data model, determine the following:**

In the following section, I will be using Node.js to provide examples etc. RavenDB provides support for C#, Java, Python and Node.js.

- How is the data model implemented?
  - In RavenDB, data is saved purely in JSON documents. Although RavenDB is a document database, it can serve as a key-value database as well (but internally, the data is saved in the same way). The documents are stored in collections which allows faster operations when using indexes. In addition to the classic documents, RavenDB allows to store binary data as so-called attachments related to existing documents. Internally, a custom storage engine called "Voron" is implemented to store the data. It uses B+ trees for the JSON documents to organize the data efficently, for binary files it uses a special "raw data section" that is not documented further. An important aspect in RavenDB is that the transactions follow the ACID protocol for documents and BASE protocol for indexes which plays a significant role when working with the data.
  - https://ravendb.net/docs/article-page/6.0/nodejs/server/storage/storage-engine
- How can different models be linked and worked with?
  - RavenDB supports only two types of files - JSON documents and binary files. The binary files are referenced from the documents and there is not much to do with them. CSV files may be imported to RavenDB as well, but when importing CSV files, there is a specialized expected format - an example follows.
  ```csv
  @id,Name,NestedObject.Name,ArrayObject,@metadata.@collection
  Samples/1-A,Import from CSV,Inner Object,"[1,2,3,4]",Samples
  ```
  Similarly, there exists an option to import data from SQL databases - there is a migration engine that will transform the data from an existing SQL database to JSON file.
  There are many more sources that allow data importing, but the important fact is that internally, the data is always stored in JSON.
  - https://ravendb.net/docs/article-page/6.0/nodejs/studio/database/tasks/import-data/import-from-csv
- Are indexes over attributes represented in a particular data model supported?
  - Yes, indexes provide the base support for the entire RavenDB system to succesfully work. For every index, there is a LINQ-style mapping function that is converted into an Apache Lucene index that provides the quick functionality. As mentioned earlier, unlike ACID-based document transactions, indexes are available through the BASE protocol. In RavenDB, there are indexes that are created automatically to enable fast search in the documents database. On every query with unspecified index, RavenDB tries to find the best-fitting index to perform the search efficiently. If there is no index present, an autoindex may be created to perform the task as well. The best way to create indexes from cody is by using the `IAbstractIndexCreationTask`, otherwise it is better to create them directly in the studio. It is possible to index attributes, related documents, nested data, hierarchical data and spatial data. More about indexes available here:
  - https://ravendb.net/docs/article-page/6.0/nodejs/indexes/what-are-indexes
- What querying means are supported over the data expressed by the different supported models? For example, create and complete a table like this:
  - As there are just JSON documents, I will cover two approaches to the database. The first one is by using RQL - Raven Query Language. This language is similar to SQL and provides a convenient way to approach queries. The second one is by using Node.js `ravendb` module that provides a nice way to interact with the database from JavaScript and TypeScript. Note that in RQL, the syntax is a bit different - consider this example of RQL `from "Employees" select FirstName as EmployeeFirstName` vs SQL `SELECT FirstName AS EmployeeFirstName FROM Employees`. Also, note that all of the Node.js queries should be initialized in the following way:
  ```ts
  const serverUrl = 'http://localhost:8080';
  const databaseName = 'db';
  
  const store = new DocumentStore([serverUrl], databaseName);
  store.initialize();

  const session = store.openSession();
  // now, queries are available
  const q1 = session.query({}) //...
  const q2 = session.query({ indexName: "idx" }) // to use index explicitly
  ```
  Also, keep in mind that there are many ways to achieve the results in Node.js, those are just the most common ways to get them.
  - https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/how-to-query


| Type of construct                 | RQL                      | Node.js                                          |
| --------------------------------- | ------------------------ | ------------------------------------------------ |
| Projection                        | select                   | session.query() //.all()                         |
| Source                            | from                     | session.query({ collection: "..." })             |
| Selection                         | where                    | q1.whereEquals('name', name) //or .whereExists() |
| Aggregation/aggregation functions | group by, count(), sum() | q1.groupBy('name') //.count()                    |
| Join                              | (load)                   | ?                                                |
| Graph Traversal  X (JOIN)         | ?                        | ?                                                |
| Unlimited Traversal               | ?                        | ?                                                |
| Optional                          | ?                        | ?                                                |
| Union                             | ?                        | ?                                                |
| Intersection                      | intersect                | q1.intersect()                                   |
| The Difference                    | ?                        | ?                                                |
| Sorting (on non/indexed columns)  | order by asc/desc        | q1.orderBy()                                     |
| Skipping                          | offset                   | q1.skip()                                        |
| Limitation                        | limit                    | q1.take() //or .first()                          |
| Distinct                          | distinct                 | q1.distinct()                                    |
| Aliasing                          | as                       | q1.selectFields()                                |
| Nesting                           | ?                        | ?                                                |
| MapReduce                         | (using indexes)          | ?                                                |

**Perform deployment of the DBMS (e.g. in Docker) and perform an experimental analysis of the querying:**

Queries with explanations are in the `queries.md` file, results in the `results.csv` file. To run the raw queries, see the `query_executor.py` file. Optionally, to run the Node.js queries, run `npm i` and then run `npx tsc query_ts_executor.ts; node --max-old-space-size=4096 query_ts_executor.js`. 

| Query   | RQL avg (ms) | Node.js avg (ms) | Node.js avg no cache (ms) |
| ------- | ------------ | ---------------- | ------------------------- |
| 3.1.1*  | ~6100        | -                | -                         |
| 3.1.2*  | ~15200       | -                | -                         |
| 3.1.3   | 120.95       | 897.6            | 1458.2                    |
| 3.1.4   | 463.45       | 13050.85         | 16205.55                  |
| 3.2.1   | 8.2          | 12.15            | 29.35                     |
| 3.2.2** | -            | -                | -                         |
| 3.3.1*  | -            | -                | -                         |
| 3.3.2   | 1950.7       | -                | -                         |
| 3.3.3   | 2630.7       | -                | -                         |
| 3.3.4** | -            | -                | -                         |
| 3.3.5** | -            | -                | -                         |
| 3.4.1** | -            | -                | -                         |
| 3.4.2   | 530.75       | 884.95           | 2875.85                   |
| 3.4.3** | -            | -                | -                         |
| 3.5.1*  | ~14300       | -                | -                         |
| 3.5.2   | 997.8        | 19288.35         | 22393.75                  |
| 3.6.1   | 799.65       | 5.05             | 1571.4                    |
| 3.7     | 99.9         | 1386.1           | 1771.95                   |

Meanings: (*) stands for manual average, because autoindex gets created automatically, (**) stands for unavailable feature

To clarify the results, caching plays a role in both of the types of queries, moreover, Node.js queries are most likely converted into less-efficient SQL/RQL queries. Also, notice that Node.js queries include the JS overhead (unlike the Python queries, including the query times directly in the result) and the result depends on the current CPU load. If needed, play around with the queries yourself. Overall, it is safe to say that raw queries perform the best.
