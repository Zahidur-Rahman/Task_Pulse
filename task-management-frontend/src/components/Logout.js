import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";

export default function LogOut() {
  const navigate = useNavigate();
  const {logout}=useAuth();

  const handleSubmit = async () => {
    await logout();
    navigate("/login"); 
  };

  return (
    <button type="button" onClick={handleSubmit} className="btn-modern btn-modern-danger" style={{padding: '6px 12px', fontSize: '0.85rem'}}>
      <i className="bi bi-box-arrow-left me-1"></i>
      Logout
    </button>
  );
}
