import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom';

export default function PredictionResults() {
  const { state } = useLocation();
  const navigate = useNavigate()
  state?.symptoms ?? navigate('/predict')

  return (
    <>
      <h2>Predicted Symptoms</h2>
    <ul>
      {state.symptoms.map((symptom: string) => <li key={symptom}>{symptom}</li>)}
    </ul>
    </>
  )
}
