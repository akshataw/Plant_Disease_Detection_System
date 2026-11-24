import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="navbar">
      <Link to="/" className="brand">
        <img src="/leaf.svg" alt="" width="28" height="28" /> LeafScan
      </Link>
      <nav>
        {user ? (
          <>
            <NavLink to="/" end>Detect</NavLink>
            <NavLink to="/history">History</NavLink>
            <span className="nav-user" title={user.email}>Hi, {user.first_name}</span>
            <button className="btn btn-link" onClick={logout}>Log out</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/register">Sign up</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
