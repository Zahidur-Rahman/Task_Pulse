import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
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
    "/user",
    JSON.stringify({
      email: signup.email,
      password: signup.password,
    })
  );
  const getAllTask = (token, page = 1, isAscending = true, limit = 5) =>
    api.get("/task/assignee/tasks", {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
      params: {
        skip: (page - 1) * limit, // Calculates how many items to skip for pagination.
        limit, // Limits the number of tasks fetched per request.
        is_ascending: isAscending, // Passes the boolean value directly for sorting
      },
    });
  

const createTask = (task, token) =>
  api.post(
    "/task",
    {
      task_title: task.title,
      description: task.description,
      is_active: task.isActive,
      slug: task.slug,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

const deleteTask = (taskId, token) =>
  api.delete(`/task/${taskId}`, {
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

const updateTask = (taskId, task, token) =>
  api.put(
    `/task/${taskId}`,

    {
      task_title: task.task_title,
      description: task.description,
      is_active: task.is_active,
      slug: task.slug,
    },

    {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

const updateTaskStatus = (taskId, status, token) =>
  api.put(
    `/task/status/${taskId}`,
    {
      status,
    },
    {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

const allAssignees = (taskId, token) =>
  api.get(`user/available-assignees/${taskId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
const changeAssignee = (taskId, assigneeEmail, token) =>
  api.put(
    `/task/change_assignee/${taskId}`,
    { task_id: taskId, assignee_email: assigneeEmail },
    { headers: { Authorization: `Bearer ${token}` } }
  );
const getTaskDetails = (id, token) =>
  api.get(`/task/${id}`, {
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
const updateTaskTitle = (id, newTitle, token) =>
  api.put(
    `/task/task_title/${id}`,
    {},
    {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`, 
      },
      params: {
        task_title: newTitle, 
      },
    }
  );

export {
  loginUser,
  SignUpUser,
  getAllTask,
  createTask,
  deleteTask,
  updateTask,
  updateTaskStatus,
  allAssignees,
  changeAssignee,
  getTaskDetails,
  updateTaskTitle,
};
