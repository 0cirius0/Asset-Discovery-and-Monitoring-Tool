import React, {useEffect} from 'react';
import logo from './logo.svg';
import './App.css';
import Dashboard from "./components/Dashboard";
import axios from 'axios';
function App() {
    useEffect(()=>{
    },[])
  return (
    <div className="App">
      <Dashboard/>
    </div>
  );
}

export default App;
