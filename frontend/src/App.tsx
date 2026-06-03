import { useEffect } from "react";
import "./App.css";
import AuthPage from "./pages/AuthPage";
import LoginFormPage from "./pages/LoginFormPage";
import { useAuthStore } from "./stores/AuthStore";

function App() {
  const { page, user, loading, goLogin, initAuth, logout } = useAuthStore();

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (page === "carousel") {
    return <AuthPage onLogin={goLogin} />;
  }

  if (page === "login") {
    return <LoginFormPage />;
  }

  return (
    <>
      <header className="App-header">
        <div className="Navbar">
          <a href="/">Home</a>
          <a href="/about">About</a>
          <a href="/contact">Contact</a>
        </div>

        <div className="Auth">
          <span>Welcome, {user?.username}!</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <div className="Container">
        <h1>Multi Agent Education</h1>
        <p>Welcome to the EduAgent Demo! ...</p>
      </div>
    </>
  );
}

export default App;