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
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await getTaskDetails(id);
        setTask(response.data);
        setNewTitle(response.data.title);
      } catch (err) {
        setError("Failed to load task details.");
        console.error(err);
      }
    };
    if (isAuthenticated) fetchTask();
  }, [id, isAuthenticated]);

  const handleTitleChange = (event) => {
    setNewTitle(event.target.value);
  };

  const handleSaveTitle = async () => {
    if (!isAuthenticated) return;

    try {
      await updateTaskTitle(id, newTitle);
      setTask((prevTask) => ({
        ...prevTask,
        title: newTitle,
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
                  <h3>{task.title}</h3>
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
                  <h5>Task Type:</h5>
                  <p className="text-capitalize">{task.task_type}</p>
                </div>
                <div className="mb-3">
                  <h5>Priority:</h5>
                  <span className={`badge ${task.priority === 'high' ? 'bg-danger' : task.priority === 'medium' ? 'bg-warning' : 'bg-success'}`}>
                    {task.priority}
                  </span>
                </div>
                <div className="mb-3">
                  <h5>Status:</h5>
                  <span className={`badge ${task.status === 'completed' ? 'bg-success' : task.status === 'in_progress' ? 'bg-primary' : 'bg-secondary'}`}>
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="mb-3">
                  <h5>Created At:</h5>
                  <p>{new Date(task.created_at).toLocaleString()}</p>
                </div>
                {task.due_date && (
                  <div className="mb-3">
                    <h5>Due Date:</h5>
                    <p>{new Date(task.due_date).toLocaleString()}</p>
                  </div>
                )}
                {task.estimated_hours > 0 && (
                  <div className="mb-3">
                    <h5>Estimated Hours:</h5>
                    <p>{task.estimated_hours}h</p>
                  </div>
                )}
                <div className="mb-3">
                  <h5>Assignee:</h5>
                  <p>{task.assignee ? `${task.assignee.first_name} ${task.assignee.last_name} (${task.assignee.email})` : "Unassigned"}</p>
                </div>
                {task.tags && task.tags.length > 0 && (
                  <div className="mb-3">
                    <h5>Tags:</h5>
                    <div>
                      {task.tags.map((tag, index) => (
                        <span key={index} className="badge bg-info me-1">{tag}</span>
                      ))}
                    </div>
                  </div>
                )}
                {task.subtasks && task.subtasks.length > 0 && (
                  <div className="mb-3">
                    <h5>Subtasks:</h5>
                    <ul className="list-group text-start">
                      {task.subtasks.map((subtask) => (
                        <li key={subtask.id} className="list-group-item d-flex justify-content-between align-items-center">
                          <span className={subtask.status === 'completed' ? 'text-decoration-line-through' : ''}>
                            {subtask.title}
                          </span>
                          <span className={`badge ${subtask.status === 'completed' ? 'bg-success' : subtask.status === 'in_progress' ? 'bg-primary' : 'bg-secondary'}`}>
                            {subtask.status.replace('_', ' ')}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
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
