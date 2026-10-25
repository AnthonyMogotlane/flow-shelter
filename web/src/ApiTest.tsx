import { useState } from "react";
import { api, setToken } from "./api";

const TEST_USER = {
  name: "TT01 Tester",
  email: "tt01-tester@example.com",
  password: "test-password-123",
};

export default function ApiTest() {
  const [log, setLog] = useState<string[]>([]);
  const add = (label: string, data: unknown) =>
    setLog((l) => [...l, `${label}: ${JSON.stringify(data, null, 2)}`]);

  async function run() {
    setLog([]);
    try {
      add("health", await api("/health"));

      try {
        add("register", await api("/auth/register", { method: "POST", body: TEST_USER }));
      } catch (e) {
        if ((e as { status?: number }).status !== 409) throw e;
        add("register", "already exists, carrying on");
      }

      const login = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: { email: TEST_USER.email, password: TEST_USER.password },
      });
      setToken(login.access_token);
      add("login", "token received");

      add("me", await api("/auth/me"));
      add("onboarding", await api("/api/onboarding"));
      add("dashboard", await api("/api/dashboard/overview"));
    } catch (e) {
      add("ERROR", e instanceof Error ? e.message : e);
    }
  }

  return (
    <div>
      <button onClick={run}>Run API test</button>
      <pre>{log.join("\n\n")}</pre>
    </div>
  );
}

