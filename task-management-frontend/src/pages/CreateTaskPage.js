import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createTask, allAssignees } from "../services/TaskService";
import { useAuth } from "../context/AuthProvider";
import Header from "../components/Header";

export default function CreateTask() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [taskType, setTaskType] = useState("task");
  const [priority, setPriority] = useState("medium");
  const [assigneeId, setAssigneeId] = useState(null);
  const [selectedAssignees, setSelectedAssignees] = useState([]);
  const [estimatedHours, setEstimatedHours] = useState(0);
  const [dueDate, setDueDate] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [tags, setTags] = useState("");
  const [assignees, setAssignees] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    if (!isAuthenticated) {
      setError("Log in again please");
      navigate("/login");
      setLoading(false);
      return;
    }
    const taskData = {
      title,
      description,
      task_type: taskType,
      priority,
      assignee_id: assigneeId || user?.id, // Primary assignee
      assignee_ids: selectedAssignees.length > 0 ? selectedAssignees : null, // Additional assignees
      estimated_hours: parseFloat(estimatedHours) || 0,
      due_date: dueDate || null,
      is_public: isPublic,
      tags: tags ? tags.split(',').map(tag => tag.trim()).filter(tag => tag).join(',') : null
    };

    try {
      const response = await createTask(taskData);
      console.log("TaskCreated", response.data);
      navigate("/dashboard");
    } catch (error) {
      console.error("Error creating task:", error);
      setError("Failed to create task. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchAssignees = async () => {
      if (isAuthenticated) {
        try {
          const response = await allAssignees();
          setAssignees(response.data || []);
        } catch (error) {
          console.error('Error fetching assignees:', error);
        }
      }
    };
    fetchAssignees();
    
    // Set current user as default assignee
    if (user?.id && assigneeId === null) {
      setAssigneeId(user.id);
      setSelectedAssignees([user.id]); // Include current user in selected assignees
    }
  }, [isAuthenticated, user, assigneeId]);
  return (
    <section className="py-5" style={{background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 50%, #81d4fa 100%)', minHeight: '100vh'}}>
      <Header />
      <div className="page-header-modern" style={{background: 'linear-gradient(135deg, #0ea5e9, #0284c7)'}}>
        <div className="container-modern">
          <h1 className="page-title-modern">Create New Task</h1>
          <p className="page-subtitle-modern">Fill in the details to create a new task</p>
        </div>
      </div>
      <div className="container-modern">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="form-modern animate-fade-in-up">
              {error && (
                <div className="alert alert-danger mt-3" role="alert">
                  {error}
                </div>
              )}
              <form onSubmit={handleSubmit}>
                <div className="form-group-modern">
                  <label htmlFor="title" className="form-label-modern">
                    Task Title *
                  </label>
                  <input
                    type="text"
                    className="form-control-modern"
                    id="title"
                    name="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    placeholder="Enter task title"
                  />
                </div>
                <div className="form-group-modern">
                  <label htmlFor="description" className="form-label-modern">
                    Description
                  </label>
                  <textarea
                    className="form-control-modern"
                    id="description"
                    name="description"
                    rows="4"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter task description"
                    style={{minHeight: '120px', resize: 'vertical'}}
                    minLength="10"
                    required
                  ></textarea>
                  <small className="form-text text-muted">Minimum 10 characters required</small>
                </div>
                <div className="row">
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label htmlFor="taskType" className="form-label-modern">
                        Task Type
                      </label>
                      <select
                        className="form-control-modern"
                        id="taskType"
                        name="taskType"
                        value={taskType}
                        onChange={(e) => setTaskType(e.target.value)}
                      >
                        <option value="task">Task</option>
                        <option value="bug">Bug</option>
                        <option value="feature">Feature</option>
                        <option value="improvement">Improvement</option>
                      </select>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label htmlFor="priority" className="form-label-modern">
                        Priority
                      </label>
                      <select
                        className="form-control-modern"
                        id="priority"
                        name="priority"
                        value={priority}
                        onChange={(e) => setPriority(e.target.value)}
                      >
                        <option value="low">🟢 Low Priority</option>
                        <option value="medium">🟡 Medium Priority</option>
                        <option value="high">🔴 High Priority</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="row">
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label htmlFor="assigneeId" className="form-label-modern">
                        Primary Assignee
                      </label>
                      <select
                        className="form-control-modern"
                        id="assigneeId"
                        name="assigneeId"
                        value={assigneeId}
                        onChange={(e) => setAssigneeId(e.target.value)}
                      >
                        <option value={user?.id}>
                          {user?.first_name} {user?.last_name} (Me - Default)
                        </option>
                        {assignees.filter(assignee => assignee.id !== user?.id).map((assignee) => (
                          <option key={assignee.id} value={assignee.id}>
                            {assignee.first_name} {assignee.last_name} ({assignee.email})
                          </option>
                        ))}
                      </select>
                      <small className="form-text text-muted">
                        The main person responsible for this task.
                      </small>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label htmlFor="selectedAssignees" className="form-label-modern">
                        Additional Assignees (Optional)
                      </label>
                      <select
                        multiple
                        className="form-control-modern"
                        id="selectedAssignees"
                        name="selectedAssignees"
                        value={selectedAssignees}
                        onChange={(e) => {
                          const values = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                          setSelectedAssignees(values);
                        }}
                        size="4"
                      >
                        {assignees.map((assignee) => (
                          <option key={assignee.id} value={assignee.id}>
                            {assignee.first_name} {assignee.last_name} ({assignee.email})
                          </option>
                        ))}
                      </select>
                      <small className="form-text text-muted">
                        Hold Ctrl/Cmd to select multiple people. Primary assignee is automatically included.
                      </small>
                    </div>
                  </div>
                </div>
                <div className="row">
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label htmlFor="estimatedHours" className="form-label-modern">
                        Estimated Hours
                      </label>
                      <input
                        type="number"
                        className="form-control-modern"
                        id="estimatedHours"
                        name="estimatedHours"
                        value={estimatedHours}
                        onChange={(e) => setEstimatedHours(e.target.value)}
                        min="0"
                        step="0.5"
                      />
                    </div>
                  </div>
                </div>
                <div className="form-group-modern">
                  <label htmlFor="dueDate" className="form-label-modern">
                    Due Date
                  </label>
                  <input
                    type="datetime-local"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="form-control"
                  />
                </div>

                {/* Tags */}
                <div className="mb-3">
                  <label className="form-label fw-bold">Tags</label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    className="form-control"
                    placeholder="Enter tags separated by commas"
                  />
                </div>

                {/* Public Checkbox */}
                <div className="mb-3 form-check">
                  <input
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="form-check-input"
                    id="publicCheckbox"
                  />
                  <label
                    className="form-check-label fw-bold"
                    htmlFor="publicCheckbox"
                  >
                    Make task public
                  </label>
                </div>

                {/* Action Buttons */}
                <div className="d-flex flex-column flex-md-row justify-content-center gap-3 mt-4">
                  <button
                    type="submit"
                    className="btn-modern btn-modern-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        {isEditing ? 'Updating...' : 'Creating...'}
                      </>
                    ) : (
                      <>
                        <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`}></i>
                        {isEditing ? 'Update Task' : 'Create Task'}
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate(-1)}
                    className="btn-modern btn-modern-secondary"
                  >
                    <i className="bi bi-arrow-left me-2"></i>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
