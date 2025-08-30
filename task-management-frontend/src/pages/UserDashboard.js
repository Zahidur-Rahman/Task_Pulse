import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthProvider';
import './UserDashboard.css';

const UserDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTimeLog, setActiveTimeLog] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showTimeLogModal, setShowTimeLogModal] = useState(false);
  
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    fetchDashboardData();
  }, [user, navigate]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/dashboard/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        throw new Error('Failed to fetch dashboard data');
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startTimeLog = async (taskId, subtaskId = null) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/dashboard/time-logs/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          task_id: taskId,
          subtask_id: subtaskId,
          start_time: new Date().toISOString()
        })
      });
      
      if (response.ok) {
        const timeLog = await response.json();
        setActiveTimeLog(timeLog);
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error starting time log:', error);
    }
  };

  const stopTimeLog = async (timeLogId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/dashboard/time-logs/${timeLogId}/stop`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setActiveTimeLog(null);
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error stopping time log:', error);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/dashboard/tasks/${taskId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (response.ok) {
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error updating task status:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Loading your dashboard...</span>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="dashboard-error">
        <h2>Failed to load dashboard</h2>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="user-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>Welcome back, {dashboardData.user.first_name}! 👋</h1>
          <p className="header-subtitle">Here's what's happening with your tasks today</p>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <div className="user-avatar">
              {dashboardData.user.first_name.charAt(0)}{dashboardData.user.last_name.charAt(0)}
            </div>
            <div className="user-details">
              <span className="user-name">{dashboardData.user.first_name} {dashboardData.user.last_name}</span>
              <span className="user-role">{dashboardData.user.user_role}</span>
            </div>
          </div>
          
          <button onClick={handleLogout} className="logout-button">
            <i className="fas fa-sign-out-alt"></i>
            Logout
          </button>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-tasks"></i>
          </div>
          <div className="stat-content">
            <h3>{dashboardData.user.total_assigned_tasks}</h3>
            <p>Total Tasks</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon completed">
            <i className="fas fa-check-circle"></i>
          </div>
          <div className="stat-content">
            <h3>{dashboardData.user.completed_tasks}</h3>
            <p>Completed</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon pending">
            <i className="fas fa-clock"></i>
          </div>
          <div className="stat-content">
            <h3>{dashboardData.user.pending_tasks}</h3>
            <p>Pending</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon overdue">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <div className="stat-content">
            <h3>{dashboardData.user.overdue_tasks}</h3>
            <p>Overdue</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon time">
            <i className="fas fa-hourglass-half"></i>
          </div>
          <div className="stat-content">
            <h3>{dashboardData.user.total_hours_logged}h</h3>
            <p>Total Hours</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon week">
            <i className="fas fa-calendar-week"></i>
          </div>
          <div className="stat-content">
            <h3>{dashboardData.total_hours_this_week}h</h3>
            <p>This Week</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="content-left">
          {/* Recent Tasks */}
          <div className="content-section">
            <div className="section-header">
              <h2>Recent Tasks</h2>
              <button 
                onClick={() => navigate('/tasks')}
                className="view-all-button"
              >
                View All
              </button>
            </div>
            
            <div className="tasks-list">
              {dashboardData.recent_tasks.map(task => (
                <div key={task.id} className="task-item">
                  <div className="task-info">
                    <h4>{task.title}</h4>
                    <div className="task-meta">
                      <span className={`priority priority-${task.priority}`}>
                        {task.priority}
                      </span>
                      <span className={`status status-${task.status.toLowerCase().replace(' ', '-')}`}>
                        {task.status}
                      </span>
                      {task.due_date && (
                        <span className={`due-date ${task.is_overdue ? 'overdue' : ''}`}>
                          <i className="fas fa-calendar"></i>
                          {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="task-actions">
                    {activeTimeLog && activeTimeLog.task_id === task.id ? (
                      <button
                        onClick={() => stopTimeLog(activeTimeLog.id)}
                        className="stop-timer-button"
                      >
                        <i className="fas fa-stop"></i>
                        Stop
                      </button>
                    ) : (
                      <button
                        onClick={() => startTimeLog(task.id)}
                        className="start-timer-button"
                      >
                        <i className="fas fa-play"></i>
                        Start
                      </button>
                    )}
                    
                    <button
                      onClick={() => {
                        setSelectedTask(task);
                        setShowTaskModal(true);
                      }}
                      className="view-task-button"
                    >
                      <i className="fas fa-eye"></i>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Deadlines */}
          <div className="content-section">
            <div className="section-header">
              <h2>Upcoming Deadlines</h2>
            </div>
            
            <div className="deadlines-list">
              {dashboardData.upcoming_deadlines.map(task => (
                <div key={task.id} className="deadline-item">
                  <div className="deadline-info">
                    <h4>{task.title}</h4>
                    <p className="deadline-date">
                      <i className="fas fa-calendar-alt"></i>
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="deadline-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${task.progress_percentage}%` }}
                      ></div>
                    </div>
                    <span className="progress-text">{task.progress_percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="content-right">
          {/* Time Tracking */}
          <div className="content-section">
            <div className="section-header">
              <h2>Time Tracking</h2>
            </div>
            
            {activeTimeLog ? (
              <div className="active-timer">
                <div className="timer-display">
                  <i className="fas fa-clock"></i>
                  <span>Timer Running</span>
                </div>
                <button
                  onClick={() => stopTimeLog(activeTimeLog.id)}
                  className="stop-timer-button large"
                >
                  <i className="fas fa-stop"></i>
                  Stop Timer
                </button>
              </div>
            ) : (
              <div className="no-active-timer">
                <i className="fas fa-play-circle"></i>
                <p>No active timer</p>
                <span>Start a task to begin tracking time</span>
              </div>
            )}
          </div>

          {/* Today's Time Logs */}
          <div className="content-section">
            <div className="section-header">
              <h2>Today's Time Logs</h2>
            </div>
            
            <div className="time-logs-list">
              {dashboardData.time_logs_today.length > 0 ? (
                dashboardData.time_logs_today.map(log => (
                  <div key={log.id} className="time-log-item">
                    <div className="log-info">
                      <span className="log-time">
                        {new Date(log.start_time).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                      <span className="log-duration">
                        {log.duration_hours > 0 ? `${log.duration_hours.toFixed(1)}h` : 'Active'}
                      </span>
                    </div>
                    <span className="log-status">
                      {log.is_active ? 'Running' : 'Completed'}
                    </span>
                  </div>
                ))
              ) : (
                <p className="no-logs">No time logs for today</p>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="content-section">
            <div className="section-header">
              <h2>Quick Actions</h2>
            </div>
            
            <div className="quick-actions">
              <button
                onClick={() => navigate('/tasks/create')}
                className="quick-action-button"
              >
                <i className="fas fa-plus"></i>
                Create Task
              </button>
              
              <button
                onClick={() => navigate('/time-logs')}
                className="quick-action-button"
              >
                <i className="fas fa-history"></i>
                View History
              </button>
              
              <button
                onClick={() => navigate('/analytics')}
                className="quick-action-button"
              >
                <i className="fas fa-chart-bar"></i>
                Analytics
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Task Modal */}
      {showTaskModal && selectedTask && (
        <div className="modal-overlay" onClick={() => setShowTaskModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedTask.title}</h3>
              <button 
                onClick={() => setShowTaskModal(false)}
                className="close-button"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="task-details">
                <p><strong>Status:</strong> {selectedTask.status}</p>
                <p><strong>Priority:</strong> {selectedTask.priority}</p>
                <p><strong>Progress:</strong> {selectedTask.progress_percentage}%</p>
                {selectedTask.due_date && (
                  <p><strong>Due Date:</strong> {new Date(selectedTask.due_date).toLocaleDateString()}</p>
                )}
              </div>
              
              <div className="task-actions-modal">
                <button
                  onClick={() => updateTaskStatus(selectedTask.id, 'In Progress')}
                  className="action-button"
                  disabled={selectedTask.status === 'In Progress'}
                >
                  Start Working
                </button>
                
                <button
                  onClick={() => updateTaskStatus(selectedTask.id, 'Completed')}
                  className="action-button completed"
                  disabled={selectedTask.status === 'Completed'}
                >
                  Mark Complete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDashboard; 