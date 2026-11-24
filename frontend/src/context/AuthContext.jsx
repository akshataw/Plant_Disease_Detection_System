import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, setAuthLostHandler, tokens } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(tokens.access));

  useEffect(() => {
    setAuthLostHandler(() => setUser(null));
    if (!tokens.access) return;
    // A 401 means the session is gone (request() already cleared the tokens). Anything else, e.g. a
    // 502 while the backend restarts, is retried briefly instead of logging the user out.
    let cancelled = false;
    const loadUser = (retriesLeft) =>
      api
        .me()
        .then((u) => {
          if (!cancelled) setUser(u);
        })
        .catch((err) => {
          if (err.status === 401 || retriesLeft <= 0 || cancelled) return;
          return new Promise((r) => setTimeout(r, 2000)).then(() => loadUser(retriesLeft - 1));
        });
    loadUser(3).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleTokens = useCallback((data) => {
    tokens.set(data);
    setUser(data.user);
    return data.user;
  }, []);

  const login = useCallback((email, password) => api.login({ email, password }).then(handleTokens), [handleTokens]);
  const register = useCallback((form) => api.register(form).then(handleTokens), [handleTokens]);
  const logout = useCallback(() => {
    tokens.clear();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
