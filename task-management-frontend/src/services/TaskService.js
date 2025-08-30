import axios from "axios";

const API_BASE_URL = 'http://127.0.0.1:7000/api/v1';
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Enable sending cookies with requests
});

// Add request interceptor to include Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

const loginUser = (login) =>
  api.post(
    "/login/token",
    new URLSearchParams({
      username: login.email,
      password: login.password,
    }),
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded", // Override for form data
      },
    }
  );

const SignUpUser = (signup) =>
  api.post(
    "/user/",
    {
      email: signup.email,
      password: signup.password,
      first_name: signup.firstName || "User",
      last_name: signup.lastName || "Name",
      role: "user"
    }
  );
  const getAllTask = (page = 1, isAscending = true, limit = 5) =>
    api.get("/task/assignee/tasks", {
      headers: {
        Accept: "application/json",
      },
      params: {
        skip: (page - 1) * limit, // Calculates how many items to skip for pagination.
        limit, // Limits the number of tasks fetched per request.
        is_ascending: isAscending, // Passes the boolean value directly for sorting
      },
    });
  

const createTask = (task) =>
  api.post(
    "/task/",
    {
      title: task.title,
      description: task.description || "",
      task_type: task.task_type || "task",
      priority: task.priority || "medium",
      assignee_id: parseInt(task.assignee_id),
      assignee_ids: task.assignee_ids || null,
      estimated_hours: parseFloat(task.estimated_hours) || 0.0,
      start_date: task.start_date || null,
      due_date: task.due_date || null,
      is_public: task.is_public || false,
      tags: task.tags || null
    }
  );

// Admin task creation endpoint
const createAdminTask = (task) =>
  api.post(
    `/admin/task`,
    {
      title: task.title,
      description: task.description || "",
      task_type: task.task_type || "task",
      priority: task.priority || "medium",
      status: task.status || "pending",
      assignee_id: parseInt(task.assignee_id),
      assignee_ids: task.assignee_ids || null,
      estimated_hours: parseFloat(task.estimated_hours) || 0.0,
      start_date: task.start_date || null,
      due_date: task.due_date || null,
      is_public: task.is_public || false,
      tags: task.tags || null
    }
  );

const deleteTask = (taskId) =>
  api.delete(`/task/${taskId}`, {
    headers: {
      Accept: "application/json",
    },
  });

const updateTask = (taskId, task) =>
  api.put(
    `/task/${taskId}`,
    {
      title: task.title,
      description: task.description,
      task_type: task.task_type,
      priority: task.priority,
      estimated_hours: task.estimated_hours,
      start_date: task.start_date,
      due_date: task.due_date,
      is_public: task.is_public,
      tags: task.tags
    },
    {
      headers: {
        Accept: "application/json",
      },
    }
  );

const updateTaskStatus = (taskId, status) =>
  api.put(
    `/task/status/${taskId}`,
    {
      status,
    },
    {
      headers: {
        Accept: "application/json",
      },
    }
  );

const allAssignees = () =>
  api.get(`/user/`);
const changeAssignee = (taskId, assigneeEmail) =>
  api.put(
    `/task/change_assignee/${taskId}`,
    { task_id: taskId, assignee_email: assigneeEmail }
  );
const getTaskDetails = (id) =>
  api.get(`/task/${id}`, {
    headers: {
      Accept: "application/json",
    },
  });
const updateTaskTitle = (id, newTitle) =>
  api.put(
    `/task/task_title/${id}?task_title=${encodeURIComponent(newTitle)}`,
    {},
    {
      headers: {
        Accept: "application/json",
      },
    }
  );

// Additional API functions for new backend features
const getUserProfile = () =>
  api.get("/user/profile");

const getUserDashboard = () =>
  api.get("/dashboard");

const getAdminDashboard = () =>
  api.get("/admin/dashboard");

const createSubtask = (taskId, subtask) =>
  api.post(
    `/task/${taskId}/subtasks`,
    {
      title: subtask.title,
      description: subtask.description,
      assignee_id: subtask.assignee_id,
      priority: subtask.priority || "medium",
      estimated_hours: subtask.estimated_hours || 0,
      due_date: subtask.due_date,
      order_index: subtask.order_index || 0
    }
  );

const startTimeLog = (timeLog) =>
  api.post(
    "/time-logs/start",
    {
      task_id: timeLog.task_id,
      subtask_id: timeLog.subtask_id,
      start_time: timeLog.start_time,
      description: timeLog.description
    }
  );

const stopTimeLog = (timeLogId) =>
  api.put(
    `/time-logs/${timeLogId}/stop`,
    {}
  );

const addTaskComment = (taskId, comment) =>
  api.post(
    `/task/${taskId}/comments`,
    {
      content: comment.content,
      is_internal: comment.is_internal || false
    }
  );

// Logout function to clear JWT cookie
const logoutUser = () =>
  api.post("/login/logout");

// Create aliases for functions with different names
const getAllUsers = allAssignees;
const getTask = getTaskDetails;
const registerUser = SignUpUser;

export {
  getAllTask,
  createTask,
  createAdminTask,
  deleteTask,
  updateTask,
  updateTaskStatus,
  getTask,
  getTaskDetails,
  getUserDashboard,
  getAdminDashboard,
  getAllUsers,
  allAssignees,
  changeAssignee,
  updateTaskTitle,
  getUserProfile,
  createSubtask,
  startTimeLog,
  stopTimeLog,
  addTaskComment,
  loginUser,
  registerUser,
  SignUpUser,
  logoutUser,
};
