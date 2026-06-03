import AuthCarousel from "../components/AuthCarousel/AuthCarousel";
import GhostMouse from "../components/GhostMouse/GhostMouse";
interface AuthPageProps {
  onLogin: () => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onLogin }) => {
  return (
    <div style={{ minHeight: "100vh", position: "relative" }}>
      <GhostMouse />
      <header
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          height: "64px",
          display: "flex",
          justifyContent: "flex-end",
          alignItems: "center",
          padding: "0 2rem",
          zIndex: 10,
          pointerEvents: "none",
        }}
      >
        <button
          onClick={onLogin}
          style={{
            pointerEvents: "auto",
            padding: "0.6rem 1.2rem",
            borderRadius: "999px",
            border: "1px solid rgba(0,0,0,0.12)",
            background: "rgba(255,255,255,0.8)",
            backdropFilter: "blur(8px)",
            cursor: "pointer",
          }}
        >
          Login
        </button>
      </header>

        <main
        style={{
            minHeight: "100vh",
            display: "grid",
            placeContent: "center",
            overflow: "visible",
        }}
        >
            <AuthCarousel />
        </main>
    </div>
  );
};

export default AuthPage;