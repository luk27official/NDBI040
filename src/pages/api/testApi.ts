import type { NextApiRequest, NextApiResponse } from 'next';
import { DocumentStore } from "ravendb";

export default async function handle(
    req: NextApiRequest,
    res: NextApiResponse,
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    // get data from GET request
    const { name, age } = req.query;

    if (!name || !age) {
        return res.status(400).json({ message: 'Missing name or age' });
    }

    if (Number.isNaN(age)) {
        return res.status(400).json({ message: 'Age must be a number' });
    }

    const result = await runRavenDBExample(name.toString(), Number(age));

    if (result) {
        return res.status(200).json({ message: 'Success', data: result });
    }

    return res.status(500).json({ message: 'Request failed' });
}

// Function to work with RavenDB
export async function runRavenDBExample(name: string, age: number) {
    // Define your RavenDB server URL and database name
    // get env variables
    let serverUrl: string = "";

    if (process.env.RAVENDB_PRODUCTION_URL === undefined) {
        serverUrl = 'http://localhost:8080';
    } else {
        serverUrl = process.env.RAVENDB_PRODUCTION_URL;
    }
    const databaseName = 'db';

    // Initialize the document store
    const store = new DocumentStore([serverUrl], databaseName);
    store.initialize();

    try {
        // Open a session
        const session = store.openSession();

        // Create a new document
        const newUser = {
            "name": name,
            "age": age,
            "@metadata": {
                "@collection": "users"
            }
        };

        // Store the document
        await session.store(newUser);
        await session.saveChanges();

        // Query for documents
        const query = session.query({})
            .whereEquals('name', name)
            .all();
        const results = await query;

        // Close the session
        session.dispose();

        return results;
    } catch (err) {
        console.error('Error:', err);
        return false;
    } finally {
        // Dispose of the store when done
        store.dispose();
    }
}