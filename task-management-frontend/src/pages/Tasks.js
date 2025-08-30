import { useNavigate, Link } from "react-router-dom";
import Header from "../components/Header.js";
import LogOut from "../components/Logout.js";
import NewTask from "../components/NewTask.js";
import React, { useEffect, useState } from "react";
import {
  getAllTask,
  deleteTask,
  updateTask,
  allAssignees,
  changeAssignee,
  updateTaskStatus,
} from "../services/TaskService.js";
import { useAuth } from "../context/AuthProvider.js";

export default function Tasks() {
  const { isAuthenticated } = useAuth();
  const { logout } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const [editingTask, setEditingTask] = useState(null);
  const [editedData, setEditedData] = useState({});
  const [showModal, setShowmodal] = useState(false);
  const [showAssigneeModal, setShowAssigneeModal] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [availableAssignees, setAvailableAssignees] = useState([]);
  const [isAscending, setIsAscending] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  const navigate = useNavigate();

  // Centralized token validation
  const ensureAuthenticated = () => {
    if (!isAuthenticated) {
      setError("You need to log in first.");
      navigate("/login");
      return false;
    }
    return true;
  };

  // Fetch available assignees
  const fetchAvailableAssignees = async (taskId) => {
    if (!ensureAuthenticated()) return;
    try {
      const response = await allAssignees();
      setAvailableAssignees(response.data);
    } catch (err) {
      setError("Failed to load available assignees.");
      console.error(err.response?.data || err);
    }
  };

  // Fetch all tasks
  useEffect(() => {
    const fetchTasks = async () => {
      if (!ensureAuthenticated()) {
        navigate("/login");
        return;
      }
      try {
        const response = await getAllTask(page, isAscending);
        console.log(response);
        setTasks(response.data.tasks);
        setTotalPages(Math.ceil(response.data.total / response.data.limit));
      } catch (err) {
        setError("Failed to load tasks.");
        console.error(err.response?.data || err);
      }
    };
    if (isAuthenticated) fetchTasks();
  }, [isAuthenticated, page, isAscending]);

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditedData((prev) => ({ ...prev, [name]: value }));
  };

  const handleEditSubmit = async () => {
    if (!ensureAuthenticated()) return;
    try {
      await updateTask(editingTask.id, editedData);
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === editingTask.id ? { ...task, ...editedData } : task
        )
      );
      setEditingTask(null);
      setError(null);
    } catch (err) {
      setError("Failed to update the task.");
      console.error(err.response?.data || err);
    }
  };

  const handleDelete = async (taskId) => {
    if (!ensureAuthenticated()) return;
    try {
      await deleteTask(taskId);
      setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
    } catch (err) {
      setError("Failed to delete the task.");
      console.error(err.response?.data || err);
    }
  };

  const handleStatusUpdate = async (status) => {
    if (!ensureAuthenticated() || !currentTask) return;
    try {
      await updateTaskStatus(currentTask.id, status);
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === currentTask.id ? { ...task, status } : task
        )
      );
      closeModal();
    } catch (err) {
      setError("Failed to update task status.");
      console.error(err.response?.data || err);
    }
  };

  const handleAssigneeChange = async (assigneeEmail) => {
    if (!ensureAuthenticated() || !currentTask) return;
    try {
      await changeAssignee(currentTask.id, assigneeEmail);
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === currentTask.id
            ? {
                ...task,
                assignee: { ...task.assignee, email: assigneeEmail },
              }
            : task
        )
      );
      closeModalAssignee();
    } catch (err) {
      setError("Failed to change assignee.");
      console.error(err.response?.data || err);
    }
  };

  const startEditing = (task) => {
    setEditingTask(task);
    setEditedData(task);
  };

  const openModal = (task) => {
    setCurrentTask(task);
    setShowmodal(true);
  };

  const openAssigneeModal = (task) => {
    setCurrentTask(task);
    fetchAvailableAssignees(task.id);
    setShowAssigneeModal(true);
  };

  const closeModal = () => {
    setShowmodal(false);
    setCurrentTask(null);
  };

  const closeModalAssignee = () => {
    setShowAssigneeModal(false);
    setCurrentTask(null);
  };

  const handleNextPage = () => {
    if (page < totalPages) setPage((prev) => prev + 1);
  };

  const handlePrevPage = () => {
    if (page > 1) setPage((prev) => prev - 1);
  };

  return (
    <section id="tasks">
      <Header />

      <div className="container pb-md-5 pb-3 " style={{ marginTop: "66px" }}>
        <h2 className="text-center">All Tasks</h2>

        {error && (
          <div className="alert alert-danger my-3" role="alert">
            {error}
          </div>
        )}
        <div className="d-flex justify-content-between align-items-center mb-1">
          <button
            onClick={() => setIsAscending(!isAscending)}
            className="btn btn-secondary btn-sm mb-1"
          >
            Sort Task: {isAscending ? "Ascending" : "Descending"}
          </button>
          <LogOut />
        </div>

        <div className="table-responsive">
          <table className="table table-striped table-hover table-bordered mt-3">
            <thead className="text-center">
              <tr scope="col">
                <th style={{ width: "15%" }}>Title</th>
                <th style={{ width: "23%" }}>Description</th>
                <th style={{ width: "17%" }}>Assigned At</th>
                <th style={{ width: "10%" }}>Status</th>
                <th style={{ width: "15%" }}>Assignee</th>
                <th style={{ width: "5%" }}>Active</th>
                <th style={{ width: "15%" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id}>
                  <td>{task.task_title}</td>
                  <td className="description">{task.description}</td>
                  <td>{task.assigned_at}</td>
                  <td>
                    {task.status}
                    <button
                      onClick={() => openModal(task)}
                      className="btn btn-sm btn-info"
                    >
                      Change
                    </button>
                  </td>
                  <td>
                    {task.assignee.email}
                    <button
                      onClick={() => openAssigneeModal(task)}
                      type="button"
                      className="btn btn-info btn-sm"
                    >
                      Change
                    </button>
                  </td>
                  <td>{task.is_active ? "Yes" : "No"}</td>
                  <td>
                    <button
                      onClick={() => handleDelete(task.id)}
                      className="btn btn-sm btn-light border border-dark m-1"
                    >
                      Delete
                      <span>
                        <i className="bi bi-trash-fill"></i>
                      </span>
                    </button>
                    <a href="#edit">
                      <button
                        onClick={() => startEditing(task)}
                        className="btn btn-sm btn-light border border-dark m-1"
                      >
                        Edit
                        <span>
                          <i className="bi bi-pencil-fill ms-1"></i>
                        </span>
                      </button>
                    </a>
                    <button
                      onClick={() => navigate(`/task_details/${task.id}`)}
                      className="btn btn-light btn-sm border border-dark m-1"
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mb-2 d-flex justify-content-between align-items-center">
          <div>
            <button
              onClick={handlePrevPage}
              disabled={page === 1}
              className="me-2 btn btn-sm btn-primary"
            >
              Previous
            </button>
            <button
              onClick={handleNextPage}
              disabled={page === totalPages}
              className="btn btn-sm btn-primary"
            >
              Next
            </button>

            <p className="fw-bold mb-0">
              Page {page} of {totalPages}
            </p>
          </div>

          {!editingTask && <NewTask />}

        </div>

        {showModal && (
          <div className="modal-overlay">
            <div
              className="modal fade show"
              style={{ display: "block" }}
              aria-labelledby="exampleModalLabel"
              role="dialog"
            >
              <div className="modal-dialog" role="document">
                <div className="modal-content">
                  <div className="modal-header">
                    <h5 className="modal-title">
                      Change Status for: {currentTask?.task_title}
                    </h5>
                  </div>
                  <div className="modal-body">
                    <ul className="list-group">
                      <li className="list-group-item">
                        <button
                          onClick={() => handleStatusUpdate("Pending")}
                          className="btn btn-warning w-100"
                        >
                          Pending
                        </button>
                      </li>
                      <li className="list-group-item">
                        <button
                          onClick={() => handleStatusUpdate("In Progress")}
                          className="btn btn-primary w-100"
                        >
                          In Progress
                        </button>
                      </li>
                      <li className="list-group-item">
                        <button
                          onClick={() => handleStatusUpdate("Completed")}
                          className="btn btn-success w-100"
                        >
                          Completed
                        </button>
                      </li>
                    </ul>
                  </div>
                  <div className="modal-footer">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={closeModal}
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {editingTask && (
          <section id="edit" className="">
            <div className="container py-md-5 py-5 mt-5">
              <div className="row">
                <div className="col-12 col-md-8 offset-md-2">
                  <div className="card p-4 p-sm-3 shadow-lg border-secondary bg-secondary text-center text-light">
                    <h2 className="fw-bold">Edit Task</h2>
                    <form className="mt-3 text-start">
                      <h4 style={{ color: "white" }} className="fw-bold">
                        Editing Task : <span>{editingTask.task_title}</span>
                      </h4>
                      <div className="mb-3">
                        <label className="form-label fw-bold ">Title</label>

                        <input
                          type="text"
                          name="task_title"
                          value={editedData.task_title || ""}
                          onChange={handleEditChange}
                          className="form-control  w-50 w-sm-75"
                        />
                      </div>

                      <div className="mb-3">
                        <label className="form-label fw-bold">
                          Description
                        </label>

                        <textarea
                          name="description"
                          value={editedData.description || ""}
                          onChange={handleEditChange}
                          className="form-control  w-50 w-sm-75"
                          style={{
                            height: "20vh",
                            resize: "none",
                          }}
                        />
                      </div>
                      <div className="mb-3">
                        <button
                          type="button"
                          onClick={handleEditSubmit}
                          className="btn btn-info me-2"
                        >
                          Submit
                        </button>

                        <button
                          onClick={() => setEditingTask(null)}
                          className="btn btn-light"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Show Assignee Modal */}
        {showAssigneeModal && (
          <div
            className="modal fade show"
            style={{ display: "block" }}
            tabIndex="-1"
            role="dialog"
            aria-labelledby="assigneeModalLabel"
            aria-hidden="true"
          >
            <div className="modal-dialog modal-dialog-centered" role="document">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title" id="assigneeModalLabel">
                    Change Assignee for: {currentTask?.task_title}
                  </h5>
                </div>
                <div className="modal-body">
                  {/* Custom Scrollable Assignee Dropdown */}
                  <div className="assignee-select-container">
                    <div className="custom-dropdown">
                      <button className="dropdown-button">
                        Select Assignee
                      </button>
                      <ul className="dropdown-list">
                        {availableAssignees.map((assignee) => (
                          <li
                            key={assignee.id}
                            className="dropdown-item"
                            onClick={() => handleAssigneeChange(assignee.email)}
                          >
                            {assignee.email}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={closeModalAssignee}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
