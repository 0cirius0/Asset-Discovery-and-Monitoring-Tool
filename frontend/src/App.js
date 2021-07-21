
import './App.css';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  // Link
} from "react-router-dom";
import Login from './component/login/Login'
import Info from './component/Info/Info'
import Computer from './component/Computer'
import Dashboard from './component/Dashboard';
import UserLogins from './component/UserLogins'
import ComputerData from './component/ComputerData';
import UserData from './component/UserData'
function App() {
  
  
  return (
    <div className="App">
     <Router>
  
      <Switch>
        
        <Route exact path="/">
          <Login />
        </Route>
        <Route path = "/Computer">
        <Computer/>
        </Route>
        <Route path = "/Info">
        <Info />
        </Route>
        <Route path="/Dashboard">
          <Dashboard />
          
        </Route>
        <Route path = "/Users">
        <UserData />
        </Route>
      
      </Switch>
      

    </Router>
   
    </div>
  );
}

export default App;
