import React from 'react'
import { Link } from 'react-router-dom'
import GraphsPage from './graphs/graphs'
import "./homepage.css"

export default function Homepage () {
  return (
    <div className="homepage" style={{ height: '100%'} }>
      <GraphsPage />
    </div> 
  )
    
}

