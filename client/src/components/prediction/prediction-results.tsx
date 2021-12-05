import React from "react";
import { Container } from "react-bootstrap";
import { useLocation, useNavigate } from "react-router-dom";

export default function PredictionResults() {
  const { state } = useLocation();
  const navigate = useNavigate();
  state?.symptoms ?? navigate("/predict");

  return (
    <>
      <Container>
        <h2>Predicted Symptoms</h2>
        <p>
          Based on the information you have provided, your predicted symptoms
          are:
        </p>
        <ul>
          {state.symptoms.map((symptom: string) => (
            <li key={symptom}>{symptom}</li>
          ))}
        </ul>

        <p>
          You can mitigate this by applying a cool cloth to the area and moving
          the arm. Make sure to drink a lot of fluids.
        </p>
      </Container>
    </>
  );
}
