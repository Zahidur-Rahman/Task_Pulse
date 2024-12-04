import { useParams, useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { getTaskDetails, updateTaskTitle } from "../services/TaskService.js";
import { useAuth } from "../context/AuthProvider.js";
import Header from "../components/Header.js";


export default function TaskDetails() {
  const { id } = useParams();
  const [task, setTask] = useState(null);
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await getTaskDetails(id, token);
        setTask(response.data);
        setNewTitle(response.data.task_title);
      } catch (err) {
        setError("Failed to load task details.");
        console.error(err);
      }
    };
    if (token) fetchTask();
  }, [id]);

  const handleTitleChange = (event) => {
    setNewTitle(event.target.value);
  };

  const handleSaveTitle = async () => {
    if (!token) return;

    try {
      await updateTaskTitle(id, newTitle, token);
      setTask((prevTask) => ({
        ...prevTask,
        task_title: newTitle,
      }));
      setIsEditing(false);
    } catch (err) {
      setError("Failed to update task title.");
      console.error(err);
    }
  };

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  if (!task) {
    return <p>Loading...</p>;
  }

  return (
    <section id="taskDetails" className="py-5 mt-5">
      <Header/>
      <div className="container">
        <div className="row">
          <div className="col-md-8 offset-md-2">
            <div className="card p-4 shadow text-center">
              <h2 className="mb-4">Task Details</h2>
              <div>
                {isEditing ? (
                  <input
                    type="text"
                    value={newTitle}
                    onChange={handleTitleChange}
                    className="form-control mb-3"
                    autoFocus
                  />
                ) : (
                  <h3>{task.task_title}</h3>
                )}
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="btn btn-outline-primary btn-sm me-2"
                >
                  {isEditing ? "Cancel" : "Edit"}
                </button>
                {isEditing && (
                  <button
                    onClick={handleSaveTitle}
                    className="btn btn-success btn-sm"
                  >
                    Save
                  </button>
                )}
              </div>
              <div className="mt-4">
                <div className="mb-3">
                  <h5>Description:</h5>
                  <p>{task.description}</p>
                </div>
                <div className="mb-3">
                  <h5>Slug:</h5>
                  <p>{task.slug}</p>
                </div>
                <div className="mb-3">
                  <h5>Assigned At:</h5>
                  <p>{new Date(task.assigned_at).toLocaleString()}</p>
                </div>
                <div className="mb-3">
                  <h5>Status:</h5>
                  <p>{task.status}</p>
                </div>
                <div className="mb-3">
                  <h5>Active:</h5>
                  <p>{task.is_active ? "Yes" : "No"}</p>
                </div>
                <div className="mb-3">
                  <h5>Assignee:</h5>
                  <p>{task.assignee?.email || "Unassigned"}</p>
                </div>
                <button
                  onClick={() => navigate(-1)}
                  className="btn btn-info btn-sm mt-3"
                >
                  Go Back
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
