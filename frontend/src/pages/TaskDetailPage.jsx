import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { addComment, getTask, updateTask } from "../api/workflow.js";
import StatusBadge from "../components/StatusBadge.jsx";

const STATUSES = ["To Do", "In Progress", "In Review", "Done"];
const PRIORITIES = ["Low", "Medium", "High", "Urgent"];

export default function TaskDetailPage() {
  const { id } = useParams();
  const [task, setTask] = useState(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");

  function load() {
    getTask(id).then(setTask).catch((e) => setError(e.message));
  }
  useEffect(load, [id]);

  async function apply(patch) {
    setError("");
    try {
      await updateTask(id, patch);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function submitComment(e) {
    e.preventDefault();
    if (!comment.trim()) return;
    try {
      await addComment(id, comment);
      setComment("");
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  if (!task) return <p className="muted">Loading…</p>;

  return (
    <div>
      <div className="page-head">
        <h1>#{task.id} {task.title}</h1>
        <StatusBadge value={task.status} />
      </div>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card">
        <p>{task.description || "No description"}</p>
        <p className="muted">
          Project #{task.project_id} · Priority: {task.priority} · Assignee:{" "}
          {task.assignee_id ? `#${task.assignee_id}` : "unassigned"} · Due: {task.due_date || "—"}
        </p>
      </div>

      <div className="card row">
        <label>
          Status
          <select value={task.status} onChange={(e) => apply({ status: e.target.value })}>
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select value={task.priority} onChange={(e) => apply({ priority: e.target.value })}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </label>
        <label>
          Due date
          <input type="date" value={task.due_date || ""} onChange={(e) => apply({ due_date: e.target.value })} />
        </label>
      </div>

      <h2>Comments</h2>
      <form className="card form" onSubmit={submitComment}>
        <textarea rows={3} value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Add a comment…" />
        <button className="btn btn-primary" type="submit">Post comment</button>
      </form>
      <ul className="comments">
        {task.comments.map((c) => (
          <li key={c.id} className="card">
            <p>{c.body}</p>
            <p className="muted">User #{c.author_id} · {new Date(c.created_at).toLocaleString()}</p>
          </li>
        ))}
      </ul>

      <h2>Activity</h2>
      <ul className="timeline">
        {task.events.map((ev) => (
          <li key={ev.id}>
            <span className="muted">{new Date(ev.created_at).toLocaleString()}</span> — <strong>{ev.event_type}</strong>
            {ev.detail ? `: ${ev.detail}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
