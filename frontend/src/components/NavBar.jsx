import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">Team Workflow Manager</Link>
        {user && (
          <nav className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/projects">Projects</Link>
            <span className="user-chip">{user.full_name}</span>
            <button
              className="btn btn-ghost"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Logout
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}
