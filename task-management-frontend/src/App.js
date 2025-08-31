import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthProvider';
import './App.css';

// Import pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TasksPage from './pages/TasksPage';
import AdminDashboard from './pages/AdminDashboard';
import AdminTaskList from './pages/AdminTaskList';
import HomePage from './pages/HomePage';
import CreateTaskPage from './pages/CreateTaskPage';
import TaskDetails from './components/TaskDetails';
import SignUp from './components/SignUp';

// Import components
import Header from './components/Header';
import Logout from './components/Logout';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

// Admin Route Component
const AdminRoute = ({ children }) => {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      {children}
    </ProtectedRoute>
  );
};

function App() {
  const { isAuthenticated, user } = useAuth();

  return (
    <Router>
      <div className="App">
        {isAuthenticated && <Header />}
        
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={
            isAuthenticated ? (
              user?.role === 'admin' ? 
                <Navigate to="/admin/dashboard" replace /> : 
                <Navigate to="/dashboard" replace />
            ) : (
              <HomePage />
            )
          } />
          
          <Route path="/login" element={
            isAuthenticated ? (
              user?.role === 'admin' ? 
                <Navigate to="/admin/dashboard" replace /> : 
                <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage />
            )
          } />
          
          {/* Protected User Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          
          <Route path="/tasks" element={
            <ProtectedRoute>
              <TasksPage />
            </ProtectedRoute>
          } />
          
          <Route path="/newtask" element={
            <ProtectedRoute>
              <CreateTaskPage />
            </ProtectedRoute>
          } />
          
          <Route path="/task/:id" element={
            <ProtectedRoute>
              <TaskDetails />
            </ProtectedRoute>
          } />
          
          <Route path="/task/:id/edit" element={
            <ProtectedRoute>
              <CreateTaskPage />
            </ProtectedRoute>
          } />
          
          <Route path="/signup" element={
            !isAuthenticated ? <SignUp /> : <Navigate to="/dashboard" replace />
          } />
          
          {/* Protected Admin Routes */}
          <Route path="/admin" element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          } />
          
          <Route path="/admin/dashboard" element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          } />
          
          <Route path="/admin/tasks" element={
            <AdminRoute>
              <AdminTaskList />
            </AdminRoute>
          } />
          
          {/* Logout Route */}
          <Route path="/logout" element={<Logout />} />
          
          {/* Catch all route */}
          <Route path="*" element={
            isAuthenticated ? (
              user?.role === 'admin' ? 
                <Navigate to="/admin/dashboard" replace /> : 
                <Navigate to="/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
