import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardSummary } from "../api/workflow.js";

const CARDS = [
  ["to_do", "To Do"],
  ["in_progress", "In Progress"],
  ["in_review", "In Review"],
  ["done", "Done"],
  ["overdue", "Overdue"],
];

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    dashboardSummary().then(setSummary).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="stat-grid">
        {CARDS.map(([key, label]) => (
          <div className={`card stat ${key === "overdue" ? "stat-overdue" : ""}`} key={key}>
            <span className="stat-value">{summary ? summary[key] : "–"}</span>
            <span className="stat-label">{label}</span>
          </div>
        ))}
      </div>
      <p className="muted">
        Total tasks: {summary ? summary.total : "–"} · <Link to="/projects">Go to projects</Link>
      </p>
    </div>
  );
}
