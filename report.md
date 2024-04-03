**Perform a static analysis of the supported data models and query languages. Specifically, for each
supported data model, determine the following:**

In the following section, I will be using Node.js to provide examples etc. RavenDB provides support for C#, Java, Python and Node.js.

- How is the data model implemented?
  - In RavenDB, data is saved purely in JSON documents. Although RavenDB is a document database, it can serve as a key-value database as well (but internally, the data is saved in the same way). The documents are stored in collections which allows faster operations when using indexes. In addition to the classic documents, RavenDB allows to store binary data as so-called attachments related to existing documents. Internally, a custom storage engine called "Voron" is implemented to store the data. It uses B+ trees for the JSON documents to organize the data efficently, for binary files it uses a special "raw data section" that is not documented further. An important aspect in RavenDB is that the transactions follow the ACID protocol for documents and BASE protocol for indexes.
  - https://ravendb.net/docs/article-page/6.0/nodejs/server/storage/storage-engine
- How can different models be linked and worked with?
  - RavenDB supports only two types of files - JSON documents and binary files. The binary files are referenced from the documents and there is not much one may do with these. CSV files may be imported to RavenDB as well, but when importing CSV files, there is a specialized expected format - an example follows.
  ```csv
  @id,Name,NestedObject.Name,ArrayObject,@metadata.@collection
  Samples/1-A,Import from CSV,Inner Object,"[1,2,3,4]",Samples
  ```
  Similarly, there exists an option to import data from SQL databases - there is a migration engine that will transform the data from an existing SQL database to JSON file. There are many more sources that allow data importing, but internally, the data is always stored in JSON. This means that there is just one type of queries.
  - https://ravendb.net/docs/article-page/6.0/nodejs/studio/database/tasks/import-data/import-from-csv
- Are indexes over attributes represented in a particular data model supported?
  - Yes, indexes provide the base support for the entire RavenDB system to succesfully work. For every index, there is a LINQ-style mapping function that is converted into an Apache Lucene index that provides the quick functionality. As mentioned earlier, unlike ACID-based document transactions, indexes are available through the BASE protocol. In RavenDB, there are indexes that are created automatically to enable fast search in the documents database. On every query with unspecified index, RavenDB tries to find the best-fitting index to perform the search efficiently. The best way to create indexes is by using the `IAbstractIndexCreationTask`. It is possible to index attributes, related documents, nested data, hierarchical data and spatial data. More about indexes available here:
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
| Join                              | (include)                | ?                                                |
| Graph Traversal  X (JOIN)         | (include)                | ?                                                |
| Unlimited Traversal               | ?                        | ?                                                |
| Optional                          | (include)                | ?                                                |
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

**Perform deployment of the DBMS (e.g. in Docker) and perform an experimental analysis of the
querying:**

For example, deploy a database system in Docker, prepare the dataset (IMDb/Yelp) for querying and
measure the times needed to execute each query (3.1 - 7) below, if possible. Run each query 20 times,
remove the minimum/maximum and then determine the average time (or standard deviation).
Assumptions:
- Queries can be trivial and should be trivial, i.e. don't use aggregation in a projection query, don't add
join in an aggregation query, etc.
- The goal is to verify the performance of a particular aspect of querying, e.g. just aggregation
(independent of other constructs) or conjunction

**3.1. Selection, Projection, Source of data**
3.1.1 Filtering on a non-indexed column, exact match, e.g., select actor with the name "Arnold" (attribute
name is not indexed!)
SELECT * FROM Actors WHERE name = "Arnold";
3.1.2 Filtering on a non-indexed column, range query, e.g., select actors with salary between 25000 and
35000 (once again, column "salary" is not indexed!)
SELECT * FROM Actors WHERE salary BETWEEN '25000' AND '35000';
3.1.3 Filtering on indexed column, exact match, e.g., select actor with age equal to 30 (attribute age is
indexed!)
SELECT * FROM Actors WHERE age = 30;
3.1.4 Filtering on indexed column, range query, e.g., select actors with age between 30 and 45 (attribute
age is indexed!)
SELECT * FROM Actors WHERE age BETWEEN '30' AND '45';

**3.2 Aggregation**
3.2.1 Use aggregation function count, e.g., count number of actors per age
SELECT age, COUNT(*) AS actorsCount FROM Actors GROUP BY age;
3.2.2 Similarly, express a query for aggregate function MAX

**3.3 Join (or graph traversal)**

3.3.1 Joining / traversal where two entities are connected by non-indexed columns, e.g., join movies and
actors where movies were filmed in the same year as actor was born
SELECT *
FROM Actors AS a INNER JOIN Movies AS m ON a.year_of_birth = m.year;
3.3.2 Joining / traversal over indexed column, e.g., find names of all actors in each movie
3.3.3 Complex join involving multiple JOINS, e.g., over 5+ tables or graph traversal over 3 types of node
labels and 2 types of edge labels
Complex query with JOINS to retrieve order details
SELECT *
FROM Actor a
 JOIN
 Acts am ON a.customerId = aa.customerId
 JOIN
 Movie m ON am.movieId = m.movieId
 JOIN
 Directed dm ON m.movieId = dn.movieId
 JOIN
 Director d ON d.directorId = dm.directorId;
MATCH (a:Actor)-[am:Acts]->(m:Movie-[dn:Directed]->(d:Director))
RETURN ...
3.3.4 Recursive query, e.g., find all direct and indirect relationships between people
SQL: WITH RECURSIVE query
3.3.5 Optional traversal
SQL: LEFT OUTER JOIN
Cypher: OPTIONAL MATCH
Get a list of all people and their friend count (0 if they have no friends)
SELECT P1.personId,
 P1.firstName,
 P1.lastName,
 COUNT(P2.personId) AS friendCount
FROM Person P1
 LEFT OUTER JOIN Person_Person PP on P1.personId = PP.personId1
 LEFT OUTER JOIN Person P2 on PP.personId2 = P2.personId
GROUP BY P1.personId;

**3.4 Set operations**
3.4.1 Union, e.g., get a list of contacts (email and phone) for both Actors and Directors
3.4.2 Intersection, e.g., get a list of shared contacts between actors and directors
3.4.3 Difference, e.g., find a list of contacts that are exclusive for directors (e.g., no actors has the same
contact)

**3.5 Sorting**
3.5.1 Sorting over non-indexed column, e.g., sort actors by salary
SELECT * FROM Actors ORDER BY salary;
3.5.2 Sorting over indexed column, e.g., sort actors by age
SELECT * FROM Actors ORDER BY age;

**3.6 Distinct**
3.6.1 Apply distinct, e.g., find unique combinations of name,surname in the table of Actors
SELECT DISTINCT name, surname FROM Actors;

**3.7 MapReduce** (or equivalent aggregation), e.g., find the number of movies played by actor and only
those who have played at least in 1 movie

The result of this phase will be a table/graph with average of measured times, e.g.: **add a csv table**