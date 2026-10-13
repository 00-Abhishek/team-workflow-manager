import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createProject, listProjects } from "../api/workflow.js";

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState({ name: "", description: "" });
  const [error, setError] = useState("");

  function load() {
    listProjects().then(setProjects).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await createProject(form);
      setForm({ name: "", description: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h1>Projects</h1>
      {error && <div className="alert alert-error">{error}</div>}

      <form className="card form" onSubmit={handleCreate}>
        <div className="row">
          <label>
            New project name
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required minLength={2} />
          </label>
          <label>
            Description
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <button className="btn btn-primary" type="submit">Create project</button>
        </div>
      </form>

      <div className="project-grid">
        {projects.map((p) => (
          <Link key={p.id} to={`/projects/${p.id}`} className="card project-card">
            <strong>{p.name}</strong>
            <span className="muted">{p.description || "No description"}</span>
          </Link>
        ))}
        {projects.length === 0 && <p className="muted">No projects yet — create one above.</p>}
      </div>
    </div>
  );
}
