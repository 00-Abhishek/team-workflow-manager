import { request } from "./client.js";

export const listProjects = () => request("/api/projects");
export const createProject = (payload) => request("/api/projects", { method: "POST", body: payload });
export const getProject = (id) => request(`/api/projects/${id}`);
export const addMember = (id, payload) => request(`/api/projects/${id}/members`, { method: "POST", body: payload });
export const projectSummary = (id) => request(`/api/projects/${id}/summary`);

export function listTasks(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== "" && v !== undefined && v !== null) query.append(k, v);
  });
  const qs = query.toString();
  return request(`/api/tasks${qs ? `?${qs}` : ""}`);
}

export const getTask = (id) => request(`/api/tasks/${id}`);
export const createTask = (projectId, payload) =>
  request(`/api/projects/${projectId}/tasks`, { method: "POST", body: payload });
export const updateTask = (id, payload) => request(`/api/tasks/${id}`, { method: "PATCH", body: payload });
export const addComment = (id, body) => request(`/api/tasks/${id}/comments`, { method: "POST", body: { body } });
export const dashboardSummary = () => request("/api/dashboard/summary");
export const listUsers = () => request("/api/users");
