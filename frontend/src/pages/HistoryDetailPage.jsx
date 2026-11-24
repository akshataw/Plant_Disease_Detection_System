import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client.js";
import AuthImage from "../components/AuthImage.jsx";
import ResultCard from "../components/ResultCard.jsx";

export default function HistoryDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.historyItem(id).then(setResult).catch((err) => setError(err.message));
  }, [id]);

  async function remove() {
    if (!window.confirm("Delete this prediction and its image?")) return;
    try {
      await api.deleteHistoryItem(id);
      navigate("/history", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  if (error) return <p className="error">{error} · <Link to="/history">Back to history</Link></p>;
  if (!result) return <p className="muted">Loading…</p>;

  return (
    <div>
      <div className="page-actions">
        <Link to="/history">← Back to history</Link>
        <button className="btn btn-danger" onClick={remove}>Delete</button>
      </div>
      <div className="upload-grid">
        <div className="card">
          <AuthImage src={result.image_url} alt={result.disease_name} className="detail-image" />
          <p className="muted">Analysed {new Date(result.prediction_date).toLocaleString()}</p>
        </div>
        <ResultCard result={result} />
      </div>
    </div>
  );
}
