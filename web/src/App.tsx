
import { useState } from "react";
import "./App.css";
import DevLogin from "./DevLogin";
import FinancialHealthCheck from "./FinancialHealthCheck";
import Commitments from "./Commitments";
import GoalsPage from "./screens/Goals";
import { DashboardProvider } from "./DashboardContext";
import { getToken, setToken } from "./api";
import Welcome from "./components/Welcom";

type Screen = "welcome" | "health" | "commitments" | "goals";

function App() {
  const [signedIn, setSignedIn] = useState(() => Boolean(getToken()));
  const [screen, setScreen] = useState<Screen>("welcome");

  if (!signedIn) {
    return (
      <>
        <Welcome
          teamName="NewTech"
          appName="FlowShelter"
          slogan="Plan for the days between paydays"
        />
        <div style={{ textAlign: "center", padding: "1rem" }}>
          <DevLogin onDone={() => setSignedIn(true)} />
        </div>
      </>
    );
  }

  return (
    <DashboardProvider>
      <nav
        aria-label="Main navigation"
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 10,
          padding: 16,
          background: "#f8fafc",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        <button onClick={() => setScreen("welcome")}>Welcome</button>
        <button onClick={() => setScreen("health")}>
          Financial health check
        </button>
        <button onClick={() => setScreen("commitments")}>
          Essential commitments
        </button>
        <button onClick={() => setScreen("goals")}>
          Savings goals
        </button>
        <button
          onClick={() => {
            setToken(null);
            setSignedIn(false);
            setScreen("welcome");
          }}
        >
          Sign out
        </button>
      </nav>

      {screen === "welcome" && (
        <Welcome
          teamName="NewTech"
          appName="FlowShelter"
          slogan="Plan for the days between paydays"
        />
      )}

      {screen === "health" && <FinancialHealthCheck />}
      {screen === "commitments" && <Commitments />}
      {screen === "goals" && <GoalsPage />}
    </DashboardProvider>
  );
}

export default App;
