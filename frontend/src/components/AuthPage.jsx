import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";

const authContent = {
  login: {
    title: "Sign in to your EDR workspace",
    subtitle: "Use your local analyst account to access alerts, activity, and response controls.",
    button: "Login",
    footerText: "Need an account?",
    footerLinkLabel: "Create one",
    footerLinkTo: "/signup"
  },
  signup: {
    title: "Create your analyst account",
    subtitle: "Set up access for this local EDR instance and continue into the dashboard.",
    button: "Create Account",
    footerText: "Already have an account?",
    footerLinkLabel: "Sign in",
    footerLinkTo: "/login"
  }
};

export default function AuthPage({ mode }) {
  const navigate = useNavigate();
  const copy = useMemo(() => authContent[mode], [mode]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setMessage(mode === "signup" ? "Creating account..." : "Signing in...");
    try {
      if (mode === "signup") {
        await api.signup(email, password);
      }
      await api.login(email, password);
      navigate("/app");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-shell simple-auth-shell">
      <section className="simple-auth-card">
        <p className="eyebrow">Automated EDR</p>
        <h1>{copy.title}</h1>
        <p className="auth-subtitle">{copy.subtitle}</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="analyst@example.com"
              required
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimum 8 characters"
              minLength={8}
              required
            />
          </label>

          <button type="submit" disabled={busy}>
            {busy ? "Working..." : copy.button}
          </button>
        </form>

        <p className={`auth-message${message && !message.includes("...") ? " is-error" : ""}`}>{message}</p>
        <p className="auth-footer">
          {copy.footerText} <Link to={copy.footerLinkTo}>{copy.footerLinkLabel}</Link>
        </p>
      </section>
    </div>
  );
}
