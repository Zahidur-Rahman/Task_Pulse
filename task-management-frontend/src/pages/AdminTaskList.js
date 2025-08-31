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
      <div className="container-fluid py-4" style={{ marginTop: '80px', minHeight: '100vh' }}>
        <div className="mb-4">
          <h2 className="mb-1">All Tasks</h2>
          <p className="text-muted mb-0">System-wide Task Management</p>
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
                <table className="table table-hover table-striped">
                  <thead className="table-light">
                    <tr>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Title</th>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Author</th>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Status</th>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Priority</th>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Assignee</th>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Due Date</th>
                      <th style={{ fontSize: '1rem', padding: '1rem' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map((task) => (
                      <tr key={task.id} style={{ fontSize: '1rem' }}>
                        <td style={{ padding: '1rem' }}>
                          <div>
                            <div style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.25rem' }}>
                              {task.title}
                            </div>
                            {task.description && (
                              <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
                                {task.description.length > 80 ? task.description.substring(0, 80) + '...' : task.description}
                              </div>
                            )}
                            <small className="text-muted">
                              ID: {task.id} | Created: {task.created_at ? new Date(task.created_at).toLocaleDateString() : 'N/A'}
                            </small>
                          </div>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span style={{ fontSize: '0.95rem' }}>
                            Author ID: {task.author_id || 'N/A'}
                          </span>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span className={`badge ${
                            task.status === 'completed' ? 'bg-success' :
                            task.status === 'in_progress' ? 'bg-primary' : 'bg-secondary'
                          }`} style={{ fontSize: '0.8rem', padding: '0.5rem 0.75rem' }}>
                            {task.status === 'completed' ? '✅ Completed' : 
                             task.status === 'in_progress' ? '⏳ In Progress' : '📋 Pending'}
                          </span>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span className={`badge ${
                            task.priority === 'high' ? 'bg-danger' :
                            task.priority === 'medium' ? 'bg-warning' : 'bg-success'
                          }`} style={{ fontSize: '0.8rem', padding: '0.5rem 0.75rem' }}>
                            {task.priority === 'high' ? '🔴 High' : 
                             task.priority === 'medium' ? '🟡 Medium' : '🟢 Low'}
                          </span>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span style={{ fontSize: '0.95rem' }}>
                            ID: {task.assignee_id || 'Unassigned'}
                          </span>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span style={{ fontSize: '0.95rem' }}>
                            {task.due_date ? new Date(task.due_date).toLocaleDateString() : 
                             <span className="text-muted">No due date</span>}
                          </span>
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <div className="btn-group" role="group">
                            <button
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => navigate(`/task/${task.id}`)}
                              title="View Details"
                              style={{ padding: '0.5rem 0.75rem' }}
                            >
                              <i className="fas fa-eye"></i>
                            </button>
                            <button
                              className="btn btn-sm btn-outline-secondary"
                              onClick={() => navigate(`/task/${task.id}/edit`)}
                              title="Edit Task"
                              style={{ padding: '0.5rem 0.75rem' }}
                            >
                              <i className="fas fa-edit"></i>
                            </button>
                          </div>
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
