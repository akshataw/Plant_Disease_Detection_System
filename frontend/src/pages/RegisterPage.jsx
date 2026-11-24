import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const field = (name) => ({ value: form[name], onChange: (e) => setForm({ ...form, [name]: e.target.value }) });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(form);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page card">
      <h1>Create account</h1>
      <form onSubmit={submit}>
        <div className="form-row">
          <label>First name<input required maxLength={100} autoComplete="given-name" {...field("first_name")} /></label>
          <label>Last name<input required maxLength={100} autoComplete="family-name" {...field("last_name")} /></label>
        </div>
        <label>Email<input type="email" required autoComplete="email" {...field("email")} /></label>
        <label>Password
          <input type="password" required minLength={8} autoComplete="new-password" {...field("password")} />
          <small className="muted">At least 8 characters</small>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn btn-primary" disabled={busy}>{busy ? "Creating…" : "Sign up"}</button>
      </form>
      <p className="muted">Already registered? <Link to="/login">Log in</Link></p>
    </div>
  );
}
