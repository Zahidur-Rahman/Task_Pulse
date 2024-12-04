import React, { useState } from "react";
import Header from "../components/Header";
import LogOut from "../components/Logout";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";
import { createTask } from "../services/TaskService";

export default function CreateTask() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isactive, setIsActive] = useState(true);
  const [slug, setSlug] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { token } = useAuth();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!token) {
      setError("Log in again please");
      navigate("/login");
      return;
    }
    const taskData = {
      title,
      description,
      isActive: isactive,
      slug,
    };

    try {
      const response = await createTask(taskData, token);
      console.log("TaskCreated", response.data);
      navigate("/tasks");
    } catch (error) {
      console.error("Error creating task:", error);
      setError("Failed to create task. Please try again.");
    }
  };

  const handleCheckboxChange = () => {
    setIsActive(!isactive);
  };
  return (
    <section>
      <Header />

      <div className="container py-md-5 py-5 " style={{ marginTop: "66px" }}>
        <div className="row">
          <div className="col-12 col-md-8 offset-md-2">
            <div className="card p-4 p-sm-3 shadow-lg border-secondary bg-secondary text-center text-light">
              {error && (
                <div className="alert alert-danger mt-3" role="alert">
                  {error}
                </div>
              )}
              <h2 className="fw-bold">New Task</h2>

              <form onSubmit={handleSubmit} className="mt-3 text-start">
                {/* Title Field */}
                <div className="mb-3">
                  <label className="form-label fw-bold ">Title</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="form-control  w-50 w-sm-75"
                  />
                </div>

                {/* Description Field */}
                <div className="mb-3">
                  <label className="form-label fw-bold">Description</label>
                  <textarea
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="form-control  w-50 w-sm-75"
                    style={{
                      height: "20vh",
                      resize: "none",
                    }}
                  ></textarea>
                </div>

                {/* Active Checkbox */}
                <div className="mb-3 form-check">
                  <input
                    type="checkbox"
                    checked={isactive}
                    onChange={handleCheckboxChange}
                    className="form-check-input"
                    id="activeCheckbox"
                  />
                  <label
                    className="form-check-label fw-bold"
                    htmlFor="activeCheckbox"
                  >
                    Active
                  </label>
                </div>

                {/* Slug Field */}
                <div className="mb-3">
                  <label className="form-label fw-bold">Slug</label>
                  <input
                    type="text"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    className="form-control  w-25 w-sm-75"
                  />
                </div>

                {/* Action Buttons */}
                <div className="d-flex flex-column flex-md-row justify-content-center">
                  <button
                    type="submit"
                    className="btn btn-primary me-md-2 mb-2 mb-md-0"
                  >
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate(-1)}
                    className="btn btn-light"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <LogOut></LogOut>
      </div>
    </section>
  );
}
