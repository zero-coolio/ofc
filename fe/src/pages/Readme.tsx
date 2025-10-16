// src/pages/Readme.tsx
import React, { useMemo } from "react";
import { Link } from "react-router-dom";

export default function Readme(){
  const storedApiBase =
    (typeof window!=="undefined" && window.localStorage.getItem("ofc_api_base")) || "";

  const swaggerUrl = useMemo(()=>{
    if(storedApiBase) return `${storedApiBase.replace(/\/+$/, "")}/docs`;
    return "https://ofc-backend-291082004564.us-central1.run.app/docs";
  },[storedApiBase]);

  return (
    <div style={{maxWidth:840,margin:"0 auto",padding:"24px"}}>
      <h1 style={{color:"#0f766e"}}>OFC Readme</h1>
      <p style={{color:"#145e5b"}}>
        This demo frontend connects to a FastAPI backend and visualizes transactions stored in SQLite.
      </p>
      <h2 style={{color:"#0f766e"}}>Quick links</h2>
      <ul>
        <li><Link to="/">Main dashboard (transactions)</Link></li>
        <li><a href={swaggerUrl} target="_blank" rel="noreferrer">Swagger API docs</a></li>
      </ul>
      <h2 style={{color:"#0f766e"}}>Overview</h2>
      <ul>
        <li>Create, list and delete transactions</li>
        <li>Filter results; the list, chart and JSON reflect the filters</li>
        <li>Left sidebar provides quick create; modify is bound to last clicked row</li>
      </ul>
        <h2 style={{color:"#0f766e"}}>Trade offs</h2>
        <ul>
            <li>No login/user account - seemed outside the scope</li>
            <li>Little validation or error checking</li>
            <li>SQlLite Db - quick installation and seeded, easy management. more time would have hooked it up to bigquery</li>
            <li>No integration with CICD, cloudrun files are created no time to test/deploy</li>
            <li>no uts</li>
            <li>bare bones front end, not time for logs/graphics</li>
            <li>react front end, fastapi python on the backend</li>
        </ul>
    </div>
  );
}
