import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { api } from "./api";
import AuthPage from "./components/AuthPage";
import SOCDashboard from "./components/SOCDashboard";

function ProtectedRoute({ children }) {
  const [ready, setReady] = useState(false);
  const [allowed, setAllowed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    let active = true;
    api
      .me()
      .then(() => {
        if (!active) {
          return;
        }
        setAllowed(true);
        setReady(true);
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setAllowed(false);
        setReady(true);
        navigate("/login", { replace: true, state: { from: location.pathname } });
      });
    return () => {
      active = false;
    };
  }, [location.pathname, navigate]);

  if (!ready) {
    return <div className="loading-screen">Checking session...</div>;
  }

  return allowed ? children : null;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/signup" element={<AuthPage mode="signup" />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <SOCDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/app" replace />} />
    </Routes>
  );
}
