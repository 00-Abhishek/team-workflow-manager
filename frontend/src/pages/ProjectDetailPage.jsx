import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  addMember,
  createTask,
  getProject,
  listTasks,
  listUsers,
  projectSummary,
  updateTask,
} from "../api/workflow.js";
import TaskCard from "../components/TaskCard.jsx";

const COLUMNS = ["To Do", "In Progress", "In Review", "Done"];
const NEXT = { "To Do": "In Progress", "In Progress": "In Review", "In Review": "Done" };

export default function ProjectDetailPage() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [filters, setFilters] = useState({ priority: "", assignee_id: "", search: "" });
  const [newTask, setNewTask] = useState({ title: "", description: "", priority: "Medium", assignee_id: "", due_date: "" });
  const [memberId, setMemberId] = useState("");
  const [error, setError] = useState("");
  const [view, setView] = useState("board");

  function load() {
    getProject(id).then(setProject).catch((e) => setError(e.message));
    projectSummary(id).then(setSummary).catch(() => {});
    listTasks({ project_id: id, ...filters }).then((d) => setTasks(d.items)).catch((e) => setError(e.message));
  }

  useEffect(() => {
    listUsers().then(setUsers).catch(() => {});
  }, []);

  useEffect(load, [id, filters]);

  const today = new Date().toISOString().slice(0, 10);

  async function handleCreateTask(e) {
    e.preventDefault();
    setError("");
    try {
      await createTask(id, {
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority,
        assignee_id: newTask.assignee_id ? Number(newTask.assignee_id) : null,
        due_date: newTask.due_date || null,
      });
      setNewTask({ title: "", description: "", priority: "Medium", assignee_id: "", due_date: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAddMember(e) {
    e.preventDefault();
    if (!memberId) return;
    setError("");
    try {
      await addMember(id, { user_id: Number(memberId) });
      setMemberId("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function advance(task) {
    const target = NEXT[task.status];
    if (!target) return;
    setError("");
    try {
      await updateTask(task.id, { status: target });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  if (!project) return <p className="muted">Loading…</p>;

  const memberIds = project.members.map((m) => m.user_id);

  return (
    <div>
      <h1>{project.name}</h1>
      <p className="muted">{project.description}</p>
      {error && <div className="alert alert-error">{error}</div>}

      {summary && (
        <div className="stat-grid">
          {[["to_do", "To Do"], ["in_progress", "In Progress"], ["in_review", "In Review"], ["done", "Done"], ["overdue", "Overdue"]].map(
            ([k, label]) => (
              <div className={`card stat ${k === "overdue" ? "stat-overdue" : ""}`} key={k}>
                <span className="stat-value">{summary[k]}</span>
                <span className="stat-label">{label}</span>
              </div>
            )
          )}
        </div>
      )}

      <div className="card">
        <h3>Members</h3>
        <p className="muted">
          {project.members.map((m) => `#${m.user_id} (${m.role})`).join(", ")}
        </p>
        <form className="row" onSubmit={handleAddMember}>
          <label>
            Add member
            <select value={memberId} onChange={(e) => setMemberId(e.target.value)}>
              <option value="">Select a user…</option>
              {users
                .filter((u) => !memberIds.includes(u.id))
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name} ({u.email})
                  </option>
                ))}
            </select>
          </label>
          <button className="btn" type="submit">Add</button>
        </form>
      </div>

      <form className="card form" onSubmit={handleCreateTask}>
        <h3>New task</h3>
        <div className="row">
          <label>
            Title
            <input value={newTask.title} onChange={(e) => setNewTask({ ...newTask, title: e.target.value })} required minLength={2} />
          </label>
          <label>
            Priority
            <select value={newTask.priority} onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}>
              {["Low", "Medium", "High", "Urgent"].map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </label>
          <label>
            Assignee
            <select value={newTask.assignee_id} onChange={(e) => setNewTask({ ...newTask, assignee_id: e.target.value })}>
              <option value="">Unassigned</option>
              {project.members.map((m) => {
                const u = users.find((x) => x.id === m.user_id);
                return (
                  <option key={m.user_id} value={m.user_id}>
                    {u ? u.full_name : `User #${m.user_id}`}
                  </option>
                );
              })}
            </select>
          </label>
          <label>
            Due date
            <input type="date" value={newTask.due_date} onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })} />
          </label>
        </div>
        <label>
          Description
          <textarea rows={2} value={newTask.description} onChange={(e) => setNewTask({ ...newTask, description: e.target.value })} />
        </label>
        <button className="btn btn-primary" type="submit">Create task</button>
      </form>

      <div className="page-head">
        <h2>Tasks</h2>
        <div className="row">
          <button className={`btn ${view === "board" ? "btn-primary" : ""}`} onClick={() => setView("board")}>Board</button>
          <button className={`btn ${view === "list" ? "btn-primary" : ""}`} onClick={() => setView("list")}>List</button>
        </div>
      </div>

      <div className="card filters">
        <input placeholder="Search tasks" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
        <select value={filters.priority} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
          <option value="">All priorities</option>
          {["Low", "Medium", "High", "Urgent"].map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <select value={filters.assignee_id} onChange={(e) => setFilters({ ...filters, assignee_id: e.target.value })}>
          <option value="">All assignees</option>
          {project.members.map((m) => (
            <option key={m.user_id} value={m.user_id}>User #{m.user_id}</option>
          ))}
        </select>
      </div>

      {view === "board" ? (
        <div className="board">
          {COLUMNS.map((col) => (
            <div className="board-col" key={col}>
              <h3>
                {col} <span className="muted">({tasks.filter((t) => t.status === col).length})</span>
              </h3>
              {tasks
                .filter((t) => t.status === col)
                .map((t) => (
                  <div key={t.id}>
                    <TaskCard task={t} overdue={t.due_date && t.due_date < today && t.status !== "Done"} />
                    {NEXT[t.status] && (
                      <button className="btn btn-mini" onClick={() => advance(t)}>
                        Move to {NEXT[t.status]}
                      </button>
                    )}
                  </div>
                ))}
            </div>
          ))}
        </div>
      ) : (
        <table className="table card">
          <thead>
            <tr><th>#</th><th>Title</th><th>Status</th><th>Priority</th><th>Assignee</th><th>Due</th></tr>
          </thead>
          <tbody>
            {tasks.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td><Link to={`/tasks/${t.id}`}>{t.title}</Link></td>
                <td>{t.status}</td>
                <td>{t.priority}</td>
                <td>{t.assignee_id ? `#${t.assignee_id}` : "—"}</td>
                <td className={t.due_date && t.due_date < today && t.status !== "Done" ? "overdue" : ""}>{t.due_date || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
