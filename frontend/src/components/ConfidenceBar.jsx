export default function ConfidenceBar({ value }) {
  const pct = Math.round((value || 0) * 100);
  const level = pct >= 80 ? "high" : pct >= 50 ? "medium" : "low";
  return (
    <div className="confidence" aria-label={`Confidence ${pct}%`}>
      <div className="confidence-track">
        <div className={`confidence-fill ${level}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="confidence-label">{pct}%</span>
    </div>
  );
}
