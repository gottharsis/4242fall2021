import React from 'react';
import logo from './logo.svg';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Homepage from './components/homepage';

function TestComponent() {
    return <div>Test Component</div>
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Homepage />} />
                <Route path="test" element={<TestComponent />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
