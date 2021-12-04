import React from "react";
import logo from "./logo.svg";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from "./components/homepage";
import PredictionForm from "./components/prediction/prediction-form";
import "bootstrap/dist/css/bootstrap.min.css";
import PredictionResults from "./components/prediction/prediction-results";
import NavigationBar from "./components/navbar/navbar";

function TestComponent() {
  return <div>Test Component</div>;
}

function App() {
  return (
    <>
      <BrowserRouter>
      <NavigationBar />
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="test" element={<TestComponent />} />
          <Route path="predict" element={<PredictionForm />} />
          <Route path="results" element={<PredictionResults />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
