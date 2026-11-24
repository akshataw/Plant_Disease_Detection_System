import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import Dropzone from "../components/Dropzone.jsx";
import ResultCard from "../components/ResultCard.jsx";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!file) return setPreview(null);
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function choose(f) {
    setFile(f);
    setResult(null);
    setError("");
  }

  async function analyse() {
    setBusy(true);
    setError("");
    try {
      setResult(await api.predict(file));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="upload-page">
      <section className="hero">
        <h1>Detect plant diseases from a leaf photo</h1>
        <p className="muted">
          Upload a clear photo of a single leaf. Our deep learning model recognises 38 conditions across 14 crops.
        </p>
      </section>

      <div className="upload-grid">
        <div className="card">
          <Dropzone onFile={choose} disabled={busy} />
          {preview && (
            <div className="preview">
              <img src={preview} alt="Selected leaf" />
              <div className="preview-actions">
                <button className="btn btn-primary" onClick={analyse} disabled={busy}>
                  {busy ? "Analysing…" : "Analyse leaf"}
                </button>
                <button className="btn btn-secondary" onClick={() => choose(null)} disabled={busy}>Clear</button>
              </div>
            </div>
          )}
          {error && <p className="error">{error}</p>}
        </div>

        {result ? <ResultCard result={result} /> : (
          <div className="card tips">
            <h3>Tips for best results</h3>
            <ul>
              <li>Photograph one leaf, filling most of the frame</li>
              <li>Use even daylight; avoid harsh shadows and blur</li>
              <li>A plain background works best</li>
              <li>Show the affected area clearly</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
