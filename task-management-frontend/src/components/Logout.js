import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";

export default function LogOut() {
  const navigate = useNavigate();
  const {logout}=useAuth();

  const handleSubmit = () => {
    logout();
    navigate("/"); 
  };

  return (
    <button type="button" onClick={handleSubmit} className="btn btn-sm btn-primary mb-1">
      Log Out

      <i className="bi bi-box-arrow-left ms-1" ></i>
    </button>
  );
}
