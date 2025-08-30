import React, { useState, useEffect } from 'react';
import { createTask, createAdminTask, allAssignees } from '../services/TaskService';
import { useAuth } from '../context/AuthProvider';

const CreateTaskModal = ({ show, onHide, onTaskCreated }) => {
  const { user, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    task_type: 'task',
    estimated_hours: 0,
    due_date: '',
    assignee_id: null,
    assignee_ids: [],
    is_public: false,
    tags: ''
  });
  const [assignees, setAssignees] = useState([]);
  const [selectedAssignees, setSelectedAssignees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (show && isAuthenticated) {
      fetchAssignees();
      // Set current user as default assignee
      if (user?.id) {
        setFormData(prev => ({ ...prev, assignee_id: user.id }));
      }
    }
  }, [show, isAuthenticated, user]);

  const fetchAssignees = async () => {
    try {
      const response = await allAssignees();
      setAssignees(response.data || []);
    } catch (error) {
      console.error('Error fetching assignees:', error);
      setAssignees([]);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setError('');
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const taskData = {
        ...formData,
        assignee_id: parseInt(formData.assignee_id) || user?.id,
        assignee_ids: selectedAssignees.length > 0 ? selectedAssignees : null
      };
      
      console.log('Creating task with data:', taskData);

      // Use admin endpoint if user is admin, otherwise use regular endpoint
      let response;
      if (user?.role === 'admin') {
        response = await createAdminTask(taskData);
      } else {
        response = await createTask(taskData);
      }
      
      console.log('Task created successfully:', response);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        task_type: 'task',
        estimated_hours: 0,
        due_date: '',
        assignee_id: user?.id || null,
        assignee_ids: [],
        is_public: false,
        tags: ''
      });
      setSelectedAssignees([]);
      
      // Close modal and refresh parent
      onHide();
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (error) {
      console.error('Error creating task:', error);
      console.error('Error details:', error.response?.data);
      setError(error.response?.data?.detail || error.message || 'Failed to create task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      task_type: 'task',
      estimated_hours: 0,
      due_date: '',
      assignee_id: user?.id || null,
      assignee_ids: [],
      is_public: false,
      tags: ''
    });
    setSelectedAssignees([]);
    setError('');
    onHide();
  };

  if (!show) return null;

  return (
    <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.6)' }} tabIndex="-1">
      <div className="modal-dialog modal-lg modal-dialog-centered" style={{ maxWidth: '800px' }}>
        <div className="modal-content" style={{ borderRadius: '15px', border: 'none', boxShadow: '0 15px 35px rgba(0,0,0,0.1)', maxHeight: '90vh', overflowY: 'auto' }}>
          
          {/* Enhanced Modal Header */}
          <div className="modal-header" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
            color: 'white', 
            borderRadius: '15px 15px 0 0',
            padding: '1.5rem 2rem'
          }}>
            <div className="d-flex align-items-center">
              <div className="bg-white bg-opacity-20 rounded-circle p-2 me-3">
                <i className="bi bi-plus-circle-fill" style={{ fontSize: '1.5rem' }}></i>
              </div>
              <div>
                <h4 className="modal-title fw-bold mb-1">Create New Task</h4>
                <p className="mb-0 opacity-75 small">Add a new task to your project workflow</p>
              </div>
            </div>
            <button 
              type="button" 
              className="btn-close btn-close-white" 
              onClick={handleClose}
              style={{ filter: 'brightness(0) invert(1)' }}
            ></button>
          </div>
          
          <div className="modal-body" style={{ padding: '1.5rem' }}>
            {error && (
              <div className="alert alert-danger d-flex align-items-center mb-3" role="alert">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              
              {/* Task Information Section - ALWAYS VISIBLE */}
              <div className="mb-3">
                <div className="bg-primary bg-opacity-10 p-2 rounded border-start border-primary border-3">
                  <h6 className="text-primary mb-1 fw-bold">
                    <i className="bi bi-info-circle-fill me-2"></i>
                    Task Information
                  </h6>
                  <p className="mb-0 text-muted small">
                    Enter the task title and description
                  </p>
                </div>
              </div>
              
              {/* Task Title - ALWAYS VISIBLE */}
              <div className="mb-3">
                <label className="form-label fw-semibold text-dark">
                  <i className="bi bi-card-text me-2 text-primary"></i>
                  Task Title *
                </label>
                <input
                  type="text"
                  className="form-control form-control-lg"
                  name="title"
                  value={formData.title || ''}
                  onChange={handleChange}
                  placeholder="Enter a clear and descriptive task title"
                  required
                  autoFocus
                  style={{
                    borderRadius: '8px',
                    border: '2px solid #e2e8f0',
                    padding: '0.75rem 1rem',
                    fontSize: '1rem',
                    backgroundColor: '#ffffff'
                  }}
                />
              </div>

              {/* Task Description - ALWAYS VISIBLE */}
              <div className="mb-3">
                <label className="form-label fw-semibold text-dark">
                  <i className="bi bi-text-paragraph me-2 text-primary"></i>
                  Task Description
                </label>
                <textarea
                  className="form-control"
                  name="description"
                  value={formData.description || ''}
                  onChange={handleChange}
                  rows="3"
                  placeholder="Describe the task in detail..."
                  style={{
                    borderRadius: '8px',
                    border: '2px solid #e2e8f0',
                    padding: '0.75rem 1rem',
                    fontSize: '0.95rem',
                    backgroundColor: '#ffffff',
                    resize: 'vertical'
                  }}
                />
              </div>

              {/* Task Settings Section */}
              <div className="mb-4">
                <div className="bg-warning bg-opacity-10 p-3 rounded-3 border-start border-warning border-4">
                  <h6 className="text-warning mb-2 fw-bold">
                    <i className="bi bi-gear-fill me-2"></i>
                    Task Configuration
                  </h6>
                  <p className="mb-0 text-muted small">
                    Set priority, type, timing, and assignment details for this task.
                  </p>
                </div>
              </div>

              <div className="row">
                {/* Priority */}
                <div className="col-md-6 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-flag-fill me-2 text-primary"></i>
                    Priority *
                  </label>
                  <select
                    className="form-control form-control-lg"
                    name="priority"
                    value={formData.priority}
                    onChange={handleChange}
                    required
                    style={{
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}
                  >
                    <option value="low">🟢 Low Priority</option>
                    <option value="medium">🟡 Medium Priority</option>
                    <option value="high">🔴 High Priority</option>
                  </select>
                </div>

                {/* Task Type */}
                <div className="col-md-6 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-bookmark-fill me-2 text-primary"></i>
                    Task Type *
                  </label>
                  <select
                    className="form-control form-control-lg"
                    name="task_type"
                    value={formData.task_type}
                    onChange={handleChange}
                    required
                    style={{
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}
                  >
                    <option value="task">📋 General Task</option>
                    <option value="feature">✨ New Feature</option>
                    <option value="bug">🐛 Bug Fix</option>
                    <option value="project">📁 Project</option>
                    <option value="maintenance">🔧 Maintenance</option>
                  </select>
                </div>

                {/* Due Date */}
                <div className="col-md-6 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-calendar-event-fill me-2 text-primary"></i>
                    Due Date
                  </label>
                  <input
                    type="date"
                    className="form-control form-control-lg"
                    name="due_date"
                    value={formData.due_date}
                    onChange={handleChange}
                    min={new Date().toISOString().split('T')[0]}
                    style={{
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}
                  />
                </div>

                {/* Estimated Hours */}
                <div className="col-md-6 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-clock-fill me-2 text-primary"></i>
                    Estimated Hours
                  </label>
                  <input
                    type="number"
                    className="form-control form-control-lg"
                    name="estimated_hours"
                    value={formData.estimated_hours}
                    onChange={handleChange}
                    min="0"
                    step="0.5"
                    placeholder="Enter estimated hours"
                    style={{
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}
                  />
                </div>
              </div>

              {/* Assignment Section */}
              <div className="mb-4">
                <div className="bg-success bg-opacity-10 p-3 rounded-3 border-start border-success border-4">
                  <h6 className="text-success mb-2 fw-bold">
                    <i className="bi bi-people-fill me-2"></i>
                    Task Assignment
                  </h6>
                  <p className="mb-0 text-muted small">
                    Assign this task to team members. Select a primary assignee and optionally add additional team members.
                  </p>
                </div>
              </div>

              <div className="row">
                {/* Primary Assignee */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-person-fill me-2 text-primary"></i>
                    Primary Assignee *
                  </label>
                  <select
                    className="form-control form-control-lg"
                    name="assignee_id"
                    value={formData.assignee_id || ''}
                    onChange={handleChange}
                    required
                    style={{
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}
                  >
                    <option value="">Select primary assignee</option>
                    {assignees.map(assignee => (
                      <option key={assignee.id} value={assignee.id}>
                        {assignee.first_name} {assignee.last_name} ({assignee.email}) {assignee.id === user?.id ? '(You)' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Additional Assignees */}
                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-people me-2 text-primary"></i>
                    Additional Assignees (Optional)
                  </label>
                  <select
                    className="form-control form-control-lg"
                    multiple
                    size="4"
                    value={selectedAssignees.map(String)}
                    onChange={(e) => {
                      const values = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                      setSelectedAssignees(values);
                    }}
                    style={{
                      borderRadius: '8px',
                      border: '2px solid #e2e8f0',
                      padding: '0.5rem',
                      fontSize: '0.95rem',
                      backgroundColor: '#ffffff',
                      minHeight: '120px'
                    }}
                  >
                    {assignees.filter(assignee => assignee.id !== parseInt(formData.assignee_id)).map(assignee => (
                      <option key={assignee.id} value={assignee.id}>
                        {assignee.first_name} {assignee.last_name} ({assignee.email}) {assignee.id === user?.id ? '(You)' : ''}
                      </option>
                    ))}
                  </select>
                  <small className="text-muted mt-1 d-block">
                    <i className="bi bi-info-circle me-1"></i>
                    Hold Ctrl/Cmd to select multiple assignees
                  </small>
                  {selectedAssignees.length > 0 && (
                    <div className="mt-2 p-2 bg-success bg-opacity-10 rounded-2 border border-success border-opacity-25">
                      <small className="text-success d-flex align-items-center">
                        <i className="bi bi-check-circle-fill me-2"></i>
                        {selectedAssignees.length} additional assignee{selectedAssignees.length > 1 ? 's' : ''} selected
                      </small>
                    </div>
                  )}
                </div>

                {/* Tags */}
                <div className="col-md-8 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-tags-fill me-2 text-primary"></i>
                    Tags
                  </label>
                  <input
                    type="text"
                    className="form-control form-control-lg"
                    name="tags"
                    value={formData.tags}
                    onChange={handleChange}
                    placeholder="e.g., frontend, urgent, review (comma separated)"
                    style={{
                      borderRadius: '12px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                    }}
                  />
                </div>

                {/* Public Task Toggle */}
                <div className="col-md-4 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-globe me-2 text-primary"></i>
                    Visibility
                  </label>
                  <div className="form-check form-switch mt-2">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="is_public"
                      name="is_public"
                      checked={formData.is_public}
                      onChange={handleChange}
                      style={{ transform: 'scale(1.2)' }}
                    />
                    <label className="form-check-label fw-medium" htmlFor="is_public">
                      Make task public
                    </label>
                    <div className="form-text">Public tasks are visible to all team members</div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="d-flex justify-content-end gap-3 mt-4 pt-3 border-top">
                <button
                  type="button"
                  className="btn btn-outline-secondary btn-lg px-4"
                  onClick={handleClose}
                  disabled={loading}
                  style={{ borderRadius: '12px' }}
                >
                  <i className="bi bi-x-circle me-2"></i>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary btn-lg px-4"
                  disabled={loading || !formData.title.trim()}
                  style={{
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
                  }}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Creating...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-plus-circle-fill me-2"></i>
                      Create Task
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateTaskModal;
