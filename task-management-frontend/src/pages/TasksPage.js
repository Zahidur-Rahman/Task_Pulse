import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider';
import { getAllTask, getAllTasksAdmin, updateTaskStatus } from '../services/TaskService';
import Header from '../components/Header';

const TasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }

      try {
        setLoading(true);
        let tasksResponse;
        
        // Use admin endpoint if user is admin, otherwise use regular endpoint
        if (user?.role === 'admin') {
          tasksResponse = await getAllTasksAdmin(1, true, 50);
        } else {
          tasksResponse = await getAllTask(1, true, 50);
        }
        
        console.log('Tasks response:', tasksResponse);
        console.log('User role:', user?.role);
        console.log('Is admin:', user?.role === 'admin');
        console.log('Response data:', tasksResponse.data);
        setTasks(Array.isArray(tasksResponse.data) ? tasksResponse.data : []);
      } catch (err) {
        console.error('Error fetching tasks:', err);
        console.error('Error details:', err.response?.data);
        console.error('Error status:', err.response?.status);
        setError(`Failed to load tasks: ${err.response?.data?.detail || err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [isAuthenticated, navigate, user]);

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      setLoading(true);
      await updateTaskStatus(taskId, newStatus);
      setLoading(false);
      // Update local state
      setTasks(tasks.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
    } catch (err) {
      console.error('Error updating task status:', err);
      setError('Failed to update task status');
    }
  };

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
      <div className="container-fluid py-4" style={{ marginTop: '80px' }}>
        {error && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            {error}
            <button type="button" className="btn-close" onClick={() => setError('')}></button>
          </div>
        )}

        {/* Page Header */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <h2 className="mb-0">All Tasks</h2>
                <p className="text-muted">
                  {user?.role === 'admin' 
                    ? 'System-wide Task Management' 
                    : 'Manage and track all your tasks'
                  }
                </p>
              </div>
              <button 
                className="btn btn-primary"
                onClick={() => navigate('/newtask')}
              >
                <i className="fas fa-plus me-2"></i>Create New Task
              </button>
            </div>
          </div>
        </div>

        {/* Tasks Table */}
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  {user?.role === 'admin' ? 'All System Tasks' : 'Your Tasks'} ({tasks.length})
                </h5>
              </div>
              <div className="card-body">
                {tasks.length === 0 ? (
                  <div className="text-center py-5">
                    <i className="fas fa-tasks fa-4x text-muted mb-3"></i>
                    <h4 className="text-muted">No tasks found</h4>
                    <p className="text-muted">You haven't created any tasks yet. Get started by creating your first task!</p>
                    <button 
                      className="btn btn-primary btn-lg"
                      onClick={() => navigate('/newtask')}
                    >
                      <i className="fas fa-plus me-2"></i>Create Your First Task
                    </button>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="table table-hover table-striped">
                      <thead className="table-light">
                        <tr>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Title</th>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Type</th>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Priority</th>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Status</th>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Assignee</th>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Due Date</th>
                          <th style={{fontSize: '1rem', padding: '1rem'}}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tasks.filter(task => task.status !== 'completed').map((task) => (
                          <tr key={task.id} className={`task-item priority-${task.priority?.toLowerCase() || 'low'}`} style={{fontSize: '1rem'}}>
                            <td style={{padding: '1rem'}}>
                              <strong style={{fontSize: '1.1rem'}}>{task.title}</strong>
                              {task.description && (
                                <>
                                  <br />
                                  <small className="text-muted" style={{fontSize: '0.9rem'}}>{task.description.substring(0, 50)}...</small>
                                </>
                              )}
                            </td>
                            <td style={{padding: '1rem'}}>
                              <span className="badge bg-secondary" style={{fontSize: '0.8rem', padding: '0.5rem 0.75rem'}}>{task.task_type || 'General'}</span>
                            </td>
                            <td style={{padding: '1rem'}}>
                              <span className={`badge priority-${task.priority?.toLowerCase() || 'low'}`} style={{fontSize: '0.8rem', padding: '0.5rem 0.75rem'}}>
                                {task.priority === 'high' ? '🔴 High' : task.priority === 'medium' ? '🟡 Medium' : '🟢 Low'}
                              </span>
                            </td>
                            <td style={{padding: '1rem'}}>
                              <select 
                                className="form-select form-select-sm"
                                value={task.status || 'pending'}
                                onChange={(e) => handleStatusChange(task.id, e.target.value)}
                                style={{fontSize: '0.9rem', minWidth: '120px'}}
                              >
                                <option value="pending">📋 Pending</option>
                                <option value="in_progress">⏳ In Progress</option>
                                <option value="completed">✅ Completed</option>
                              </select>
                            </td>
                            <td style={{padding: '1rem'}}>
                              <span style={{fontSize: '0.95rem'}}>
                                {task.assignee 
                                  ? `${task.assignee.first_name || ''} ${task.assignee.last_name || ''}`.trim()
                                  : `${user?.first_name || ''} ${user?.last_name || ''}`.trim() + ' (You)'}
                              </span>
                            </td>
                            <td style={{padding: '1rem'}}>
                              <span style={{fontSize: '0.95rem'}}>
                                {task.due_date 
                                  ? new Date(task.due_date).toLocaleDateString()
                                  : <span className="text-muted">No due date</span>}
                              </span>
                            </td>
                            <td style={{padding: '1rem'}}>
                              <div className="btn-group" role="group">
                                <button
                                  className="btn btn-sm btn-outline-primary"
                                  onClick={() => navigate(`/task/${task.id}`)}
                                  title="View Details"
                                  style={{padding: '0.5rem 0.75rem'}}
                                >
                                  <i className="fas fa-eye"></i>
                                </button>
                                <button
                                  className="btn btn-sm btn-outline-secondary"
                                  onClick={() => navigate(`/task/${task.id}/edit`)}
                                  title="Edit Task"
                                  style={{padding: '0.5rem 0.75rem'}}
                                >
                                  <i className="fas fa-edit"></i>
                                </button>
                                {task.status !== 'completed' && (
                                  <button
                                    className="btn btn-sm btn-outline-success"
                                    onClick={() => handleStatusChange(task.id, 'completed')}
                                    title="Mark Complete"
                                    style={{padding: '0.5rem 0.75rem'}}
                                  >
                                    <i className="fas fa-check"></i>
                                  </button>
                                )}
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
      </div>
    </div>
  );
};

export default TasksPage;
