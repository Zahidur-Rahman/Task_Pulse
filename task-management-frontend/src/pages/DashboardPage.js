import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider';
import { getAllTask, getUserDashboard } from '../services/TaskService';
import Header from '../components/Header';
import CreateTaskModal from '../components/CreateTaskModal';

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }

      try {
        setLoading(true);
        setError('');
        
        // Try to fetch dashboard data, but don't fail if it's not available
        try {
          const dashboardResponse = await getUserDashboard();
          setDashboardData(dashboardResponse.data);
        } catch (dashError) {
          console.warn('Dashboard API not available:', dashError);
          // Set default dashboard data if API fails
          setDashboardData({
            user: { total_tasks: 0, completed_tasks: 0, pending_tasks: 0, in_progress_tasks: 0 }
          });
        }
        
        // Fetch tasks
        try {
          const tasksResponse = await getAllTask();
          setTasks(tasksResponse.data || []);
        } catch (taskError) {
          console.warn('Tasks API error:', taskError);
          if (taskError.response?.status === 401) {
            // User is not authenticated, redirect to login
            navigate('/login');
            return;
          }
          setTasks([]);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        if (error.response?.status === 401) {
          navigate('/login');
          return;
        }
        setError('Some dashboard features may not be available');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated, navigate]);

  const fetchTasks = async () => {
    try {
      const tasksResponse = await getAllTask();
      setTasks(tasksResponse.data || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      if (error.response?.status === 401) {
        navigate('/login');
      }
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
      <div className="container-fluid py-3" style={{ marginTop: '66px', minHeight: '100vh' }}>
        {error && (
          <div className="alert alert-warning alert-dismissible fade show" role="alert">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
            <button type="button" className="btn-close" onClick={() => setError('')}></button>
          </div>
        )}
        <div className="mb-3">
          <h6 className="text-muted mb-0">Task Overview</h6>
        </div>
        {/* Dashboard Stats */}
        {dashboardData && (
          <div className="row mb-3">
            <div className="col-md-3 mb-2">
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-number">{tasks.length || 0}</div>
                <div className="dashboard-stat-label">Total Tasks</div>
              </div>
            </div>
            <div className="col-md-3 mb-2">
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-number">{tasks.filter(t => t.status === 'completed').length || 0}</div>
                <div className="dashboard-stat-label">Completed</div>
              </div>
            </div>
            <div className="col-md-3 mb-2">
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-number">{tasks.filter(t => t.status === 'in_progress').length || 0}</div>
                <div className="dashboard-stat-label">In Progress</div>
              </div>
            </div>
            <div className="col-md-3 mb-2">
              <div className="dashboard-stat-card">
                <div className="dashboard-stat-number">{tasks.filter(t => t.status === 'pending').length || 0}</div>
                <div className="dashboard-stat-label">Pending</div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Tasks Section */}
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h6 className="mb-0">Recent Tasks</h6>
                <div className="d-flex gap-2">
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="btn btn-primary btn-sm"
                  >
                    <i className="bi bi-plus me-1"></i>
                    Create Task
                  </button>
                  <button
                    onClick={() => navigate('/tasks')}
                    className="btn btn-outline-secondary btn-sm"
                  >
                    View All
                  </button>
                </div>
              </div>
              <div className="card-body" style={{ maxHeight: tasks.length > 4 ? '400px' : 'auto', overflowY: tasks.length > 4 ? 'auto' : 'visible' }}>
                {tasks.length === 0 ? (
                  <div className="text-center py-3">
                    <div className="text-muted mb-2">
                      <i className="bi bi-clipboard-x" style={{ fontSize: '2rem' }}></i>
                    </div>
                    <p className="text-muted mb-2">No tasks yet</p>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => setShowCreateModal(true)}
                    >
                      Create Task
                    </button>
                  </div>
                ) : (
                  <div className="list-group list-group-flush">
                    {tasks.slice(0, 8).map((task) => (
                      <div className="list-group-item border-0 px-0 py-2" key={task.id}>
                        <div className="d-flex justify-content-between align-items-start">
                          <div className="flex-grow-1">
                            <h6 className="mb-1 fw-medium" style={{ fontSize: '0.875rem' }}>{task.title}</h6>
                            {task.description && (
                              <p className="mb-1 text-muted" style={{ fontSize: '0.75rem' }}>
                                {task.description.length > 60 ? task.description.substring(0, 60) + '...' : task.description}
                              </p>
                            )}
                            {task.due_date && (
                              <small className="text-muted">Due: {new Date(task.due_date).toLocaleDateString()}</small>
                            )}
                          </div>
                          <div className="text-end ms-2">
                            <div className="mb-1">
                              <span className={`badge ${
                                task.priority === 'high' ? 'bg-danger' :
                                task.priority === 'medium' ? 'bg-warning' : 'bg-success'
                              }`} style={{ fontSize: '0.65rem' }}>
                                {task.priority}
                              </span>
                            </div>
                            <div>
                              <span className={`badge ${
                                task.status === 'completed' ? 'bg-success' :
                                task.status === 'in_progress' ? 'bg-primary' : 'bg-secondary'
                              }`} style={{ fontSize: '0.65rem' }}>
                                {task.status.replace('_', ' ')}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <CreateTaskModal 
        show={showCreateModal}
        onHide={() => setShowCreateModal(false)}
        onTaskCreated={() => {
          fetchTasks();
        }}
      />
    </div>
  );
};

export default DashboardPage;
