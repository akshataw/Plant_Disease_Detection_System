import { useEffect, useState } from "react";
import { api } from "../api/client.js";

// <img> tags can't send the Authorization header, so fetch the image as a blob instead.
export default function AuthImage({ src, alt, className }) {
  const [url, setUrl] = useState(null);

  useEffect(() => {
    let objectUrl;
    let cancelled = false;
    api.imageBlob(src)
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      })
      .catch(() => setUrl(null));
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src]);

  return url ? <img src={url} alt={alt} className={className} /> : <div className={`${className} img-placeholder`} />;
}
