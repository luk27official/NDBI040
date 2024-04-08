NOTE: RavenDB can only perform searches on indexed columns. This means that every search is indexed (maybe apart from the distinct search), only the first one is done whilst creating the index, so the times are really just for illustration. This means that the average is based just on 2-3 performs when there was no prior index present and one had to be created on the fly. Those were done manually in the studio.
> All queries in RavenDB use an index to provide results, even when you don't specify one.
> https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/how-to-query

**3.1.1**
Filtering on a non-indexed column, exact match (see NOTE)
RQL: `from "yelp_academic_dataset_business" where search("name", "A*")`
Node.js: Not available.

**3.1.2**
Filtering on a non-indexed column, range query (see NOTE)
RQL: `from "yelp_academic_dataset_business" where stars < 5 and stars > 2`
Node.js: Not available.

**3.1.3**
Filtering on a indexed column, exact match
RQL: `from "yelp_academic_dataset_business" where search("name", "A*")`
Node.js:
```ts
const results = await session.query({ collection: "yelp_academic_dataset_business" })
    .whereRegex("name", "^A").all();
```

**3.1.4**
Filtering on a indexed column, range query
RQL: `from "yelp_academic_dataset_business" where stars < 5 and stars > 2`
Node.js:
```ts
const results = await session.query({ collection: "yelp_academic_dataset_business" })
    .whereBetween("stars", 3, 4).all();
```

**3.2.1**
Use aggregation function count
RQL: `from "yelp_academic_dataset_user_filtered" group by "review_count" select key() as "key", count() as "Count"`
Node.js:
```ts
const results = await session.query({ collection: "yelp_academic_dataset_user_filtered" })
    .groupBy("review_count").selectKey().selectCount().all();
```

**3.2.2**
Similarly, express a query for aggregate function MAX
- max not available - we could do this with sorting, but that is described in another section
> https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/what-is-rql

**3.3.1**
Note that the joins are not really joins as the "joining" is here represented by embedding the documents by the given references.

Joining / traversal where two entities are connected by non-indexed columns (with limit of 100k, see NOTE)
RQL:
```
from "yelp_academic_dataset_tip_refs" as t
load t.reference_user_id as u
select {
    user: u.name
    text: t.text
}
limit 100000
```
Node.js: Not available.

**3.3.2**
Joining / traversal over indexed column (with limit of 100k)
RQL:
```
from "yelp_academic_dataset_tip_refs" as t
load t.reference_user_id as u
select {
    user: u.name
    text: t.text
}
limit 100000
```
Node.js: Not available.

**3.3.3**
Complex join involving multiple JOINS (with limit of 100k)
RQL:
```
from "yelp_academic_dataset_tip_refs" as t
load t.reference_user_id as u, t.reference_business_id as b
select {
    user: u.name
    text: t.text
    business_id: b.business_id
}
limit 100000
```
Node.js: Not available.

**3.3.4**
Recursive query
- I couldn't come up with a way to do this directly in RavenDB, as it is missing in the documentation. Moreover, I have no idea how to fit it onto the existing data.
> https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/what-is-rql

**3.3.5**
Optional traversal
- I couldn't come up with a way to do this directly in RavenDB, as it is missing in the documentation. Moreover, I have no idea how to fit it onto the existing data.
> https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/what-is-rql

**3.4.1**
Union
- Likely not supported, missing again
> https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/what-is-rql

**3.4.2**
Intersection
RQL: `from "yelp_academic_dataset_tip_refs" where intersect(search("text", "*chicken*"), compliment_count == 0)`
Node.js:
```ts
const results = await session.query({ collection: "yelp_academic_dataset_tip_refs" })
    .whereRegex("text", "chicken")
    .intersect()
    .whereEquals("compliment_count", 0)
    .all();
```

**3.4.3**
Difference
- Likely not supported, missing again
> https://ravendb.net/docs/article-page/6.0/nodejs/client-api/session/querying/what-is-rql

**3.5.1**
Sorting over non-indexed column (see NOTE)
RQL: `from "yelp_academic_dataset_business" order by latitude asc`
Node.js: Not available.

**3.5.2**
Sorting over indexed column
RQL: `from "yelp_academic_dataset_business" order by latitude asc`
Node.js:
```ts
const results = await session.query({ collection: "yelp_academic_dataset_business" })
    .orderBy("latitude").all();
```

**3.6.1**
Apply distinct
RQL: `from "yelp_academic_dataset_business" select distinct state`
Node.js:
```ts
const results = await session.query({ collection: "yelp_academic_dataset_business" })
    .selectFields("state").distinct().all();
```

**3.7**
MapReduce - count tips by businesses
First, a MapReduce index must be created. This is done in the Indexes tab, then select New Index. Then, paste the following.
Name: `count-tips-by-business`
Map:
```csharp
from tip in docs.yelp_academic_dataset_tip_refs
select new {
     business_id = tip.business_id,
     Count = 1
}
```
Reduce:
```csharp
from result in results
group result by result.business_id into g
select new {
   business_id = g.Key,
   Count = g.Sum(x => x.Count)
}
```
Then, the RQL query may be used: `from index "count-tips-by-business"`.
Node.js:
```ts
const results = await session.query({ indexName: "count-tips-by-business" }).all();
```
