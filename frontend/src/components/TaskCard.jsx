import { Link } from "react-router-dom";

const PRIORITY_CLASS = {
  Low: "prio prio-low",
  Medium: "prio prio-medium",
  High: "prio prio-high",
  Urgent: "prio prio-urgent",
};

export default function TaskCard({ task, overdue }) {
  return (
    <Link to={`/tasks/${task.id}`} className="card task-card">
      <div className="task-card-head">
        <span className={PRIORITY_CLASS[task.priority] || "prio"}>{task.priority}</span>
        {overdue && <span className="overdue">Overdue</span>}
      </div>
      <strong>{task.title}</strong>
      <span className="muted">
        {task.assignee_id ? `Assignee #${task.assignee_id}` : "Unassigned"}
        {task.due_date ? ` · due ${task.due_date}` : ""}
      </span>
    </Link>
  );
}
