import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider';
import { getAllTask } from '../services/TaskService';
import Header from '../components/Header';

const AdminTaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated || !user || user.role !== 'admin') {
      navigate('/login');
      return;
    }

    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await getAllTask();
        setTasks(response.data || []);
      } catch (error) {
        console.error('Error fetching tasks:', error);
        setError('Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [isAuthenticated, user, navigate]);

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="container-fluid py-3" style={{ marginTop: '66px', minHeight: '100vh' }}>
        <div className="mb-3">
          <h6 className="text-muted mb-0">All Tasks</h6>
        </div>
        
        {error && (
          <div className="alert alert-warning alert-dismissible fade show" role="alert">
            {error}
            <button type="button" className="btn-close" onClick={() => setError('')}></button>
          </div>
        )}

        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <h6 className="mb-0">Task Management</h6>
            <button
              onClick={() => navigate('/admin')}
              className="btn btn-outline-secondary btn-sm"
            >
              <i className="bi bi-arrow-left me-1"></i>
              Back to Dashboard
            </button>
          </div>
          <div className="card-body">
            {tasks.length === 0 ? (
              <div className="text-center py-4">
                <div className="text-muted mb-2">
                  <i className="bi bi-clipboard-x" style={{ fontSize: '2rem' }}></i>
                </div>
                <p className="text-muted">No tasks found</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table table-sm">
                  <thead>
                    <tr>
                      <th style={{ fontSize: '0.75rem' }}>Title</th>
                      <th style={{ fontSize: '0.75rem' }}>Status</th>
                      <th style={{ fontSize: '0.75rem' }}>Priority</th>
                      <th style={{ fontSize: '0.75rem' }}>Assignee</th>
                      <th style={{ fontSize: '0.75rem' }}>Due Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => (
                      <tr key={task.id}>
                        <td>
                          <div>
                            <div style={{ fontSize: '0.875rem', fontWeight: '500' }}>{task.title}</div>
                            {task.description && (
                              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                                {task.description.length > 50 ? task.description.substring(0, 50) + '...' : task.description}
                              </div>
                            )}
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${
                            task.status === 'completed' ? 'bg-success' :
                            task.status === 'in_progress' ? 'bg-primary' : 'bg-secondary'
                          }`} style={{ fontSize: '0.65rem' }}>
                            {task.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${
                            task.priority === 'high' ? 'bg-danger' :
                            task.priority === 'medium' ? 'bg-warning' : 'bg-success'
                          }`} style={{ fontSize: '0.65rem' }}>
                            {task.priority}
                          </span>
                        </td>
                        <td style={{ fontSize: '0.75rem' }}>
                          {task.assignee_email || 'Unassigned'}
                        </td>
                        <td style={{ fontSize: '0.75rem' }}>
                          {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminTaskList;
