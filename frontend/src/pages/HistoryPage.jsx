import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import AuthImage from "../components/AuthImage.jsx";

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true; // ignore responses for a page the user has already left
    setError("");
    api
      .history(page, 12)
      .then((d) => active && setData(d))
      .catch((err) => active && setError(err.message));
    return () => {
      active = false;
    };
  }, [page]);

  if (!data) return error ? <p className="error">{error}</p> : <p className="muted">Loading…</p>;

  return (
    <div>
      <h1>Prediction history</h1>
      {error && <p className="error">{error}</p>}
      {data.items.length === 0 ? (
        <p className="muted">No predictions yet. <Link to="/">Analyse your first leaf</Link>.</p>
      ) : (
        <div className="history-grid">
          {data.items.map((item) => (
            <Link key={item.id} to={`/history/${item.id}`} className="card history-item">
              <AuthImage src={item.image_url} alt={item.disease_name} className="history-thumb" />
              <div>
                <span className={`badge ${item.is_healthy ? "badge-healthy" : "badge-disease"}`}>
                  {item.is_healthy ? "Healthy" : "Disease"}
                </span>
                <h3>{item.disease_name}</h3>
                <p className="muted">
                  {Math.round(item.confidence * 100)}% · {new Date(item.prediction_date).toLocaleString()}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
      {data.pages > 1 && (
        <div className="pagination">
          <button className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {data.page} of {data.pages}</span>
          <button className="btn btn-secondary" disabled={page >= data.pages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </div>
  );
}
