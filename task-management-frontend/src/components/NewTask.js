import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";

export default function NewTask() {
  const navigate = useNavigate();
  const { token } = useAuth(); // Get token from context

  const handleSubmit = () => {
    if (!token) {
      // If no token, redirect to login page
      navigate("/login"); 
    } else {
      // If token exists, navigate to new task page
      navigate("/newtask");
    }
  };

  return (
    <button type="button" onClick={handleSubmit} className="btn btn-sm btn-info">
      Create Task
    </button>
  );
}
