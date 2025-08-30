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

  const handleAssigneeToggle = (assigneeId) => {
    setSelectedAssignees(prev => {
      const newSelection = prev.includes(assigneeId)
        ? prev.filter(id => id !== assigneeId)
        : [...prev, assigneeId];
      
      setFormData(prevForm => ({
        ...prevForm,
        assignee_ids: newSelection
      }));
      
      return newSelection;
    });
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
      <div className="modal-dialog modal-lg modal-dialog-centered" style={{ maxWidth: '600px' }}>
        <div className="modal-content" style={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}>
          <div className="modal-header" style={{ background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', borderRadius: '12px 12px 0 0' }}>
            <h4 className="modal-title fw-bold d-flex align-items-center">
              <i className="bi bi-plus-circle-fill me-2" style={{ fontSize: '1.2rem' }}></i>
              Create New Task
            </h4>
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
              <div className="row">
                <div className="col-12 mb-4">
                  <div className="bg-light p-3 rounded border-start border-primary border-4">
                    <h6 className="text-primary mb-2 fw-bold">
                      <i className="bi bi-info-circle-fill me-2"></i>
                      Task Information
                    </h6>
                    <p className="mb-0 text-muted small">
                      Fill in the basic details about your task including title, description, and priority level.
                    </p>
                  </div>
                </div>
                
                <div className="col-12 mb-3">
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
                      borderRadius: '10px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '1rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#0ea5e9'}
                    onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                  />
                </div>

                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold text-dark">
                    <i className="bi bi-text-paragraph me-2 text-primary"></i>
                    Task Description
                  </label>
                  <textarea
                    className="form-control"
                    name="description"
                    value={formData.description || ''}
                    onChange={handleChange}
                    rows="4"
                    placeholder="Describe the task in detail, including requirements, goals, and any important notes..."
                    style={{
                      borderRadius: '10px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      resize: 'vertical',
                      minHeight: '100px',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                  />
                </div>

                <div className="col-12 mb-4">
                  <div className="bg-light p-3 rounded border-start border-warning border-4">
                    <h6 className="text-warning mb-2 fw-bold">
                      <i className="bi bi-gear-fill me-2"></i>
                      Task Settings
                    </h6>
                    <p className="mb-0 text-muted small">
                      Configure priority, type, timing, and assignment details for this task.
                    </p>
                  </div>
                </div>

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
                      borderRadius: '10px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                  >
                    <option value="low">🟢 Low Priority</option>
                    <option value="medium">🟡 Medium Priority</option>

          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-12 mb-4">
                <div className="bg-light p-3 rounded border-start border-primary border-4">
                  <h6 className="text-primary mb-2 fw-bold">
                    <i className="bi bi-info-circle-fill me-2"></i>
                    Task Information
                  </h6>
                  <p className="mb-0 text-muted small">
                    Fill in the basic details about your task including title, description, and priority level.
                  </p>
                </div>
              </div>
              
              <div className="col-12 mb-3">
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
                    borderRadius: '10px',
                    border: '2px solid #e2e8f0',
                    padding: '0.8rem 1rem',
                    fontSize: '1rem',
                    transition: 'all 0.3s ease',
                    backgroundColor: '#ffffff',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#0ea5e9'}
                  onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                />
              </div>

              <div className="col-12 mb-3">
                <label className="form-label fw-semibold text-dark">
                  <i className="bi bi-text-paragraph me-2 text-primary"></i>
                  Task Description
                </label>
                <textarea
                  className="form-control"
                  name="description"
                  value={formData.description || ''}
                  onChange={handleChange}
                  rows="4"
                  placeholder="Describe the task in detail, including requirements, goals, and any important notes..."
                  style={{
                    borderRadius: '10px',
                    border: '2px solid #e2e8f0',
                    padding: '0.8rem 1rem',
                    fontSize: '0.95rem',
                    transition: 'all 0.3s ease',
                    backgroundColor: '#ffffff',
                    resize: 'vertical',
                    minHeight: '100px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                  }}
                />
              </div>
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
                      borderRadius: '10px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                  />
                </div>

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
                      borderRadius: '10px',
                      border: '2px solid #e2e8f0',
                      padding: '0.8rem 1rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.3s ease',
                      backgroundColor: '#ffffff',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                  />
                </div>

                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-person me-1"></i>
                    Primary Assignee *
                  </label>
                  <select
                    className="form-control"
                    name="assignee_id"
                    value={formData.assignee_id || ''}
                    onChange={handleChange}
                    required
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #d1d5db',
                      padding: '0.75rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.2s ease',
                      backgroundColor: '#f8fafc'
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

                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-people me-1"></i>
                    Additional Assignees (Optional)
                  </label>
                  <div className="border rounded p-2" style={{ backgroundColor: '#f8fafc', minHeight: '100px', maxHeight: '150px', overflowY: 'auto' }}>
                    {assignees.filter(assignee => assignee.id !== parseInt(formData.assignee_id)).length === 0 ? (
                      <p className="text-muted mb-0 text-center py-2">No additional assignees available</p>
                    ) : (
                      assignees.filter(assignee => assignee.id !== parseInt(formData.assignee_id)).map(assignee => (
                        <div key={assignee.id} className="form-check mb-1">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id={`assignee-${assignee.id}`}
                            checked={selectedAssignees.includes(assignee.id)}
                            onChange={() => {
                              setSelectedAssignees(prev => 
                                prev.includes(assignee.id)
                                  ? prev.filter(id => id !== assignee.id)
                                  : [...prev, assignee.id]
                              );
                            }}
                          />
                          <label className="form-check-label" htmlFor={`assignee-${assignee.id}`} style={{ fontSize: '0.9rem' }}>
                            <span className="fw-medium">{assignee.first_name} {assignee.last_name}</span>
                            <span className="text-muted ms-1">({assignee.email})</span>
                            {assignee.id === user?.id && <span className="text-primary ms-1">(You)</span>}
                          </label>
                        </div>
                      ))
                    )}
                  </div>
                  {selectedAssignees.length > 0 && (
                    <small className="text-success mt-1 d-block">
                      <i className="bi bi-check-circle me-1"></i>
                      {selectedAssignees.length} additional assignee{selectedAssignees.length > 1 ? 's' : ''} selected
                    </small>
                  )}
                </div>

                <div className="col-12 mb-3">
                  <label className="form-label fw-semibold">
                    <i className="bi bi-tags me-1"></i>
                    Tags
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    name="tags"
                    value={formData.tags}
                    onChange={handleChange}
                    placeholder="e.g., frontend, urgent, review"
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #d1d5db',
                      padding: '0.75rem',
                      fontSize: '0.95rem',
                      transition: 'all 0.2s ease',
                      backgroundColor: '#f8fafc'
                    }}
                  />
                </div>

                <div className="col-md-6 mb-3">
                  <div className="form-check mt-4">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      name="is_public"
                      id="is_public"
                      checked={formData.is_public}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_public: e.target.checked }))}
                    />
                    <label className="form-check-label fw-semibold" htmlFor="is_public">
                      <i className="bi bi-globe me-1"></i>
                      Make task public
                    </label>
                    <small className="text-muted d-block">Public tasks are visible to all team members</small>
                  </div>
                </div>
              </div>
            </form>
          </div>

          <div className="modal-footer" style={{ padding: '1rem 2rem', borderTop: '1px solid #e9ecef' }}>
            <button 
              type="button" 
              className="btn btn-secondary me-2" 
              onClick={handleClose}
              disabled={loading}
              style={{
                borderRadius: '8px',
                padding: '0.75rem 1.5rem',
                fontWeight: '500',
                border: 'none',
                transition: 'all 0.2s ease'
              }}
            >
              <i className="bi bi-x-circle me-1"></i>
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={loading || !formData.title.trim()}
              style={{
                borderRadius: '8px',
                padding: '0.75rem 1.5rem',
                fontWeight: '500',
                border: 'none',
                background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
                transition: 'all 0.2s ease'
              }}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Creating...
                </>
              ) : (
                <>
                  <i className="bi bi-check-lg me-1"></i>
                  Create Task
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateTaskModal;
