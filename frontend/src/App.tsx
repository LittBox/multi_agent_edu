import { useEffect } from "react";
import "./App.css";
import AuthPage from "./pages/AuthPage";
import LoginFormPage from "./pages/LoginFormPage";
import { useAuthStore } from "./stores/AuthStore";
import DashboardPage from "./pages/DashboardPage";
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
        <DashboardPage
          userId={user!.id}
          username={user?.username}
          onLogout={logout}
        />
    </>
  );
}

export default App;