async function submitAuthForm(endpoint, form) {
  const formData = new FormData(form);
  const response = await fetch(endpoint, {
    method: "POST",
    body: formData,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || "Authentication failed");
  }
  return payload;
}

function setMessage(text, isError = false) {
  const message = document.getElementById("auth-message");
  if (!message) {
    return;
  }
  message.textContent = text;
  message.style.color = isError ? "#ffacac" : "#96a6ca";
}

async function handleAuth(form, mode) {
  const button = document.getElementById("auth-submit");
  button.disabled = true;
  button.classList.add("is-loading");
  setMessage(mode === "signup" ? "Creating account..." : "Signing in...");
  try {
    if (mode === "signup") {
      await submitAuthForm("/api/auth/signup", form);
      setMessage("Account created. Signing in...");
    }
    await submitAuthForm("/api/auth/login", form);
    setMessage("Access granted. Opening dashboard...");
    window.location.href = "/dashboard";
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    button.disabled = false;
    button.classList.remove("is-loading");
  }
}

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await handleAuth(loginForm, "login");
  });
}

if (signupForm) {
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await handleAuth(signupForm, "signup");
  });
}
