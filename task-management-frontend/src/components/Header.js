import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";
import LogOut from "./Logout";

export default function Header() {
  const { user } = useAuth();
  return (
    <header id="main_menu">
      <nav className="navbar navbar-expand-md navbar-light fixed-top navbar-modern">
        <div className="container">
          <Link to={user?.role === 'admin' ? '/admin/dashboard' : '/dashboard'} className="navbar-brand d-flex">
            <img
              src="/image/logo.webp"
              alt="Logo"
              style={{ width: "35px", height: "35px" }}
              className="me-2 float-start rounded-5"
            />
            <span>
              <h4 className="fw-bold mt-1" style={{fontSize: '1.3rem'}}>TaskPulse</h4>
            </span>
          </Link>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#mainmenu"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div id="mainmenu" className="collapse navbar-collapse">
            <ul className="navbar-nav ms-auto">
              <li>
                <Link className="nav-link-modern" to={user?.role === 'admin' ? '/admin/dashboard' : '/dashboard'}>
                  Dashboard
                </Link>
              </li>
              {user?.role !== 'admin' && (
                <>
                  <li>
                    <Link className="nav-link-modern" to="/tasks">
                      My Tasks
                    </Link>
                  </li>
                </>
              )}
              <li>
                <LogOut />
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </header>
  );
}
