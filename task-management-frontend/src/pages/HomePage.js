import React from "react";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="home_page" >

      <section className="container pb-md-5 py-3 mt-5" style={{marginTop:"66px"}} >
        
        <div className="row" >

            {/* Centered Content */}
            <div style={{ height: "30vh" }}></div>
            <div
              className="col-md-8 offset-md-2 d-flex flex-column justify-content-center align-items-center"
              
            >
              <h1>TASKPULSE</h1>

              <div>
                <button
                  className="btn btn-primary me-3"
                  type="button"
                  onClick={() => navigate("/login")}
                >
                  Sign In
                </button>
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => navigate("/signup")}
                >
                  Sign Up
                </button>
              </div>
            </div>
          </div>
        
      </section>
    </div>
  );
};

export default HomePage;
