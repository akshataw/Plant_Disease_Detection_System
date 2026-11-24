import { useRef, useState } from "react";

const ACCEPT = ["image/jpeg", "image/png", "image/webp"];
export const MAX_MB = 10;

export default function Dropzone({ onFile, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  function handle(file) {
    if (!file) return;
    if (!ACCEPT.includes(file.type)) return setError("Please choose a JPG, PNG or WEBP image.");
    if (file.size > MAX_MB * 1024 * 1024) return setError(`Image must be smaller than ${MAX_MB} MB.`);
    setError("");
    onFile(file);
  }

  return (
    <div>
      <div
        className={`dropzone ${dragging ? "dragging" : ""} ${disabled ? "disabled" : ""}`}
        role="button"
        tabIndex={0}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && !disabled && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) handle(e.dataTransfer.files?.[0]);
        }}
      >
        <p className="dropzone-title">Drag &amp; drop a leaf photo here</p>
        <p className="muted">or click to browse · JPG, PNG, WEBP · max {MAX_MB} MB</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT.join(",")}
          hidden
          data-testid="file-input"
          onChange={(e) => { handle(e.target.files?.[0]); e.target.value = ""; }}
        />
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
