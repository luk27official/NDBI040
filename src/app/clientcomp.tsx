"use client";

import { useState } from "react";

export function ClientComp() {
    const [lastResult, setLastResult] = useState("No results yet");
    const [resultData, setResultData] = useState("");
    const [name, setName] = useState("");
    const [age, setAge] = useState("");

    const wrapper = async () => {
        const response = await fetch(`/api/testApi?name=${encodeURIComponent(name)}&age=${encodeURIComponent(age)}`);
        const data = await response.json();
        setLastResult(data.message);
        setResultData(JSON.stringify(data.data));
    };

    return (
        <div>
            <table>
                <tbody>
                    <tr>
                        <td>Name:</td>
                        <td><input type="text" id="name" onChange={(e) => setName(e.target.value)} style={{ color: "black" }} /></td>
                    </tr>
                    <tr>
                        <td>Age:</td>
                        <td><input type="text" id="age" onChange={(e) => setAge(e.target.value)} style={{ color: "black" }} /></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td><button onClick={() => wrapper()}>Submit</button></td>
                    </tr>
                </tbody>
            </table>
            <p>{lastResult}</p>
            <p>{resultData}</p>
        </div>
    );
}