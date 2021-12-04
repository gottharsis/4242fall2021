import React from 'react'
import { Link } from 'react-router-dom'
import GraphsPage from './graphs/graphs'

export default function Homepage () {
  return (
    <div className="homepage">
      4242 fall 2021 project homepage
      <Link to="/test"> lsdkfjdlskfj</Link>
      <GraphsPage />
    </div> 
  )
    
}

