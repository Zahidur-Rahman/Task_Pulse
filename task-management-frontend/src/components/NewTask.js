import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";

export default function NewTask() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth(); // Get authentication status from context

  const handleSubmit = () => {
    if (!isAuthenticated) {
      // If not authenticated, redirect to login page
      navigate("/login"); 
    } else {
      // If authenticated, navigate to new task page
      navigate("/newtask");
    }
  };

  return (
    <button type="button" onClick={handleSubmit} className="btn btn-sm btn-info">
      Create Task
    </button>
  );
}
