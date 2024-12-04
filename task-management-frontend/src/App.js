import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import TaskDetails from "./components/TaskDetails";
import SignIn from "./components/SignIn";
import SignUp from "./components/SignUp";
import Tasks from "./pages/Tasks";
import CreateTask from "./pages/CreateTaskPage";
import { useAuth } from "./context/AuthProvider"; // Import the Auth context


function App() {
  const { token } = useAuth(); 

  return (
    <Router>
      <Routes>

        
        <Route path="/" element={token?<Navigate to="/tasks"/>:<HomePage />} />
        
        <Route path="/login" element={!token? <SignIn/>:<Navigate to="/tasks" />} />
        <Route path="/signup" element={token?<Navigate to="/" />: <SignUp />} />
        <Route path="/tasks" element={token ? <Tasks /> : <Navigate to="/login" />} />
        <Route path="/newtask" element={token ? <CreateTask /> : <Navigate to="/login" />} />
        <Route path="/task_details/:id" element={token?<TaskDetails/>:<Navigate to="/login"/>}></Route>
      </Routes> 
    </Router>
  );
}

export default App;
