import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider';
import { getAllTask, updateTaskStatus } from '../services/TaskService';
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
        const tasksResponse = await getAllTask(1, true, 50);
        console.log('Tasks response:', tasksResponse);
        setTasks(Array.isArray(tasksResponse.data) ? tasksResponse.data : []);
      } catch (err) {
        console.error('Error fetching tasks:', err);
        setError('Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [isAuthenticated, navigate]);

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
      <div className="container-fluid py-4" style={{ marginTop: '66px' }}>
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
                <p className="text-muted">Manage and track all your tasks</p>
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
                <h5 className="mb-0">Your Tasks ({tasks.length})</h5>
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
                    <table className="table table-hover">
                      <thead>
                        <tr>
                          <th>Title</th>
                          <th>Type</th>
                          <th>Priority</th>
                          <th>Status</th>
                          <th>Assignee</th>
                          <th>Due Date</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tasks.map((task) => (
                          <tr key={task.id} className={`task-item priority-${task.priority?.toLowerCase() || 'low'}`}>
                            <td>
                              <strong>{task.title}</strong>
                              {task.description && (
                                <>
                                  <br />
                                  <small className="text-muted">{task.description.substring(0, 50)}...</small>
                                </>
                              )}
                            </td>
                            <td>
                              <span className="badge bg-secondary">{task.task_type || 'General'}</span>
                            </td>
                            <td>
                              <span className={`badge priority-${task.priority?.toLowerCase() || 'low'}`}>
                                {task.priority || 'Low'}
                              </span>
                            </td>
                            <td>
                              <span className={`badge status-${task.status?.toLowerCase().replace(' ', '-') || 'todo'}`}>
                                {task.status || 'To Do'}
                              </span>
                            </td>
                            <td>
                              {task.assignee 
                                ? `${task.assignee.first_name} ${task.assignee.last_name}`
                                : user?.first_name + ' ' + user?.last_name + ' (You)'}
                            </td>
                            <td>
                              {task.due_date 
                                ? new Date(task.due_date).toLocaleDateString()
                                : <span className="text-muted">No due date</span>}
                            </td>
                            <td>
                              <div className="btn-group" role="group">
                                <button
                                  className="btn btn-sm btn-outline-primary"
                                  onClick={() => navigate(`/task/${task.id}`)}
                                  title="View Details"
                                >
                                  <i className="fas fa-eye"></i>
                                </button>
                                <button
                                  className="btn btn-sm btn-outline-secondary"
                                  onClick={() => navigate(`/task/${task.id}/edit`)}
                                  title="Edit Task"
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
      </div>
    </div>
  );
};

export default TasksPage;
