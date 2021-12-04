import React from "react";
import { Container } from "react-bootstrap";
import "./graphs.css";

// async function fetch_graphs() {
//   const host = window.location.hostname
//   const endpoint = '/seagraph'
//   const uri = host + endpoint
//   try {
//     const response = await axios.get(uri)
//     return response.data
//   } catch (e) {
//     return "There was an error loading the graphs"
//   }
// }

export default function GraphsPage() {
  return (
      <div className="graphs-container">
        <iframe src="/seagraph" id="graph-embed" width="100%"></iframe>
      </div>
  );
}
