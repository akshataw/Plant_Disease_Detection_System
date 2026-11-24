import ConfidenceBar from "./ConfidenceBar.jsx";

function Section({ title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <section className="detail-section">
      <h3>{title}</h3>
      <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
    </section>
  );
}

export default function ResultCard({ result }) {
  const { details } = result;
  return (
    <article className="card result-card">
      <div className="result-header">
        <span className={`badge ${result.is_healthy ? "badge-healthy" : "badge-disease"}`}>
          {result.is_healthy ? "Healthy" : "Disease detected"}
        </span>
        <h2>{result.disease_name}</h2>
        {details.pathogen && <p className="muted pathogen">{details.pathogen}</p>}
        <ConfidenceBar value={result.confidence} />
      </div>

      {result.low_confidence && (
        <div className="alert alert-warning">
          The model is not very confident. Try a clearer, well-lit photo of a single leaf on a plain background.
        </div>
      )}
      {result.model_version?.includes("dummy") && (
        <div className="alert alert-warning">
          Demo model loaded — predictions are random until the trained model is installed.
        </div>
      )}

      <p className="description">{details.description}</p>
      <div className="detail-grid">
        <Section title="Symptoms" items={details.symptoms} />
        <Section title="Causes" items={details.causes} />
        <Section title="Prevention" items={details.prevention} />
        <Section title="Treatment" items={details.treatment} />
      </div>

      {result.top_k?.length > 1 && (
        <section className="detail-section">
          <h3>Other possibilities</h3>
          <ul className="alternatives">
            {result.top_k.slice(1).map((alt) => (
              <li key={alt.label}>
                <span>{alt.name}</span>
                <span className="muted">{Math.round(alt.confidence * 100)}%</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="disclaimer">
        This is general guidance. Confirm the diagnosis and follow product labels and advice from your local
        agricultural extension officer before applying any treatment.
      </p>
    </article>
  );
}
