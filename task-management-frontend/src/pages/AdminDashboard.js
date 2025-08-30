import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider';
import { getAdminDashboard } from '../services/TaskService';
import Header from '../components/Header';
import CreateTaskModal from '../components/CreateTaskModal';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const fetchDashboardData = useCallback(async () => {
    try {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }
      
      const response = await getAdminDashboard();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      // Set default data structure if API fails
      setDashboardData({
        total_users: 0,
        total_tasks: 0,
        active_tasks: 0,
        completed_tasks: 0,
        overdue_tasks: 0,
        total_hours_logged: 0,
        users_by_role: { admin: 1, user: 0 },
        tasks_by_status: { pending: 0, in_progress: 0, completed: 0 },
        tasks_by_priority: { low: 0, medium: 0, high: 0 },
        top_performers: [],
        overdue_tasks_list: []
      });
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated || !user || user.role !== 'admin') {
      navigate('/login');
      return;
    }
    
    fetchDashboardData();
  }, [user, navigate, isAuthenticated, fetchDashboardData]);


  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading admin dashboard...</span>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="admin-dashboard-error">
        <h2>Failed to load admin dashboard</h2>
        <button onClick={fetchDashboardData} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="container-fluid py-3" style={{ marginTop: '66px', minHeight: '100vh' }}>
        <div className="mb-3">
          <h6 className="text-muted mb-0">Admin Dashboard</h6>
        </div>
        <div className="row">
          <div className="col-12">
            {/* Stats Cards */}
            <div className="row mb-3">
              <div className="col-md-3 mb-2">
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-number">{dashboardData.total_users || 0}</div>
                  <div className="dashboard-stat-label">Total Users</div>
                </div>
              </div>
              <div className="col-md-3 mb-2">
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-number">{dashboardData.total_tasks || 0}</div>
                  <div className="dashboard-stat-label">Total Tasks</div>
                </div>
              </div>
              <div className="col-md-3 mb-2">
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-number">{dashboardData.active_tasks || 0}</div>
                  <div className="dashboard-stat-label">Active Tasks</div>
                </div>
              </div>
              <div className="col-md-3 mb-2">
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-number">{dashboardData.completed_tasks || 0}</div>
                  <div className="dashboard-stat-label">Completed</div>
                </div>
              </div>
            </div>

            {/* Admin Actions */}
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h6 className="mb-0">Admin Actions</h6>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="btn btn-primary btn-sm"
                >
                  <i className="bi bi-plus me-1"></i>
                  Create Task
                </button>
              </div>
              <div className="card-body">
                <div className="d-flex flex-wrap gap-2">
                  <button
                    onClick={() => navigate('/admin/tasks')}
                    className="btn btn-outline-secondary btn-sm"
                  >
                    <i className="bi bi-list-ul me-1"></i>
                    Task List
                  </button>
                  
                  <button
                    onClick={() => setShowUserModal(true)}
                    className="btn btn-outline-secondary btn-sm"
                  >
                    <i className="bi bi-people me-1"></i>
                    Manage Users
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Promote User Modal */}
        {showUserModal && (
          <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">User Management</h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setShowUserModal(false)}
                  ></button>
                </div>
                <div className="modal-body">
                  <p>User management features are coming soon!</p>
                  <p>This will include user promotion, role management, and user analytics.</p>
                </div>
                <div className="modal-footer">
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={() => setShowUserModal(false)}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <CreateTaskModal 
          show={showCreateModal}
          onHide={() => setShowCreateModal(false)}
          onTaskCreated={fetchDashboardData}
        />
    </div>
  );
};

export default AdminDashboard; 