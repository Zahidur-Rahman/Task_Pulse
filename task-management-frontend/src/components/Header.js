import React from "react";

export default function Header() {
  return (
    <header id="main_menu">
      <nav className="navbar navbar-expand-md navbar-light fixed-top navbar-custom">
        <div className="container">
          <a href="#" className="navbar-brand d-flex">
            <img
              src="/image/logo.webp"
              alt="Logo"
              style={{ width: "40px", height: "40px" }}
              className="me-2 float-start rounded-5"
            />
            <span>
              <h4 className="fw-bold mt-2">TaskPulse</h4>
            </span>
          </a>
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
                <a className="nav-link" href="#">
                  Home
                </a>
              </li>
              <li>
                <a className="nav-link" href="#">
                  About
                </a>
              </li>
              <li>
                <a className="nav-link" href="#">
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </header>
  );
}
