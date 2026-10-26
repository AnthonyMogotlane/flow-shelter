import { useEffect, useState } from "react";
import { api } from "./api";
import { useDashboard } from "./DashboardContext";

type Commitment = {
  name: string;
  amount: string;
  due_date: string;
  is_paid: boolean;
};

const inputStyle: React.CSSProperties = {
  display: "block",
  width: "100%",
  boxSizing: "border-box",
  padding: "10px",
  marginTop: "5px",
  border: "1px solid #cbd5e1",
  borderRadius: "8px",
  fontSize: "15px",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  fontWeight: 600,
  marginBottom: "12px",
};

function emptyCommitment(): Commitment {
  return { name: "", amount: "", due_date: "", is_paid: false };
}

export default function Commitments() {
  const { refresh } = useDashboard();
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [formError, setFormError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadCommitments() {
      setLoading(true);
      try {
        const result = await api<{ commitments: Commitment[] }>(
          "/api/onboarding/commitments"
        );

        if (active) {
          setCommitments(
            (result.commitments || []).map((item) => ({
              name: item.name || "",
              amount: String(item.amount ?? ""),
              due_date: item.due_date || "",
              is_paid: Boolean(item.is_paid),
            }))
          );
          setFormError("");
        }
      } catch (e) {
        if (active) {
          const err = e as Error & { status?: number };
          setFormError(
            err.status === 401 || err.status === 403
              ? "Your session may have expired. Please sign in again."
              : err.message || "Could not load your commitments."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadCommitments();
    return () => {
      active = false;
    };
  }, []);

  function updateCommitment(
    index: number,
    field: keyof Commitment,
    value: string | boolean
  ) {
    setCommitments((current) =>
      current.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    );
  }

  async function saveCommitments(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    setFormError("");

    try {
      const items = commitments.filter(
        (item) =>
          item.name.trim() ||
          item.amount.trim() ||
          item.due_date ||
          item.is_paid
      );

      for (const item of items) {
        if (!item.name.trim() || !item.amount.trim()) {
          throw new Error("Each bill needs both a name and an amount.");
        }

        const amount = Number(item.amount);
        if (!Number.isFinite(amount) || amount <= 0) {
          throw new Error("Each bill amount must be greater than zero.");
        }
      }

      await api<{ commitments: Commitment[] }>("/api/onboarding/commitments", {
        method: "PUT",
        body: {
          commitments: items.map((item) => ({
            name: item.name.trim(),
            amount: Number(item.amount),
            due_date: item.due_date || null,
            is_paid: item.is_paid,
          })),
        },
      });

      const latest = await api<{ commitments: Commitment[] }>(
        "/api/onboarding/commitments"
      );

      setCommitments(
        (latest.commitments || []).map((item) => ({
          name: item.name || "",
          amount: String(item.amount ?? ""),
          due_date: item.due_date || "",
          is_paid: Boolean(item.is_paid),
        }))
      );

      await refresh();
      setMessage("Commitments saved. Your dashboard has been refreshed.");
    } catch (e) {
      const err = e as Error & { status?: number };
      if (err.status === 401 || err.status === 403) {
        setFormError("Your session may have expired. Please sign in again.");
      } else if (err.status === 422) {
        setFormError("The API rejected some details. Check each bill and try again.");
      } else {
        setFormError(err.message || "Could not save commitments.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 850, margin: "0 auto", padding: "28px 18px", color: "#172033" }}>
      <header style={{ marginBottom: 24 }}>
        <p style={{ color: "#0f766e", fontWeight: 700, marginBottom: 6 }}>FLOWSHELTER</p>
        <h1 style={{ margin: "0 0 8px" }}>Essential commitments</h1>
        <p style={{ color: "#64748b" }}>
          Record bills that affect the money you have available between paydays.
        </p>
      </header>

      {loading ? (
        <p>Loading your saved commitments...</p>
      ) : (
        <form
          onSubmit={saveCommitments}
          style={{ background: "#fff", padding: 22, border: "1px solid #e2e8f0", borderRadius: 14 }}
        >
          <p style={{ color: "#64748b", fontSize: 14, marginTop: 0 }}>
            Add rent, transport, electricity, subscriptions or other bills.
            Mark bills as paid when you have settled them.
          </p>

          {commitments.length === 0 && (
            <p style={{ color: "#64748b" }}>
              You have no commitments saved yet. Add your first bill below.
            </p>
          )}

          {commitments.map((item, index) => (
            <section
              key={index}
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: 12,
                padding: 16,
                marginBottom: 14,
              }}
            >
              <h3 style={{ marginTop: 0 }}>Bill {index + 1}</h3>

              <label style={labelStyle}>
                Bill name
                <input
                  required
                  maxLength={100}
                  value={item.name}
                  onChange={(e) => updateCommitment(index, "name", e.target.value)}
                  placeholder="e.g. Rent"
                  style={inputStyle}
                />
              </label>

              <label style={labelStyle}>
                Amount (ZAR)
                <input
                  required
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={item.amount}
                  onChange={(e) => updateCommitment(index, "amount", e.target.value)}
                  placeholder="e.g. 4500"
                  style={inputStyle}
                />
              </label>

              <label style={labelStyle}>
                Due date (optional)
                <input
                  type="date"
                  value={item.due_date}
                  onChange={(e) => updateCommitment(index, "due_date", e.target.value)}
                  style={inputStyle}
                />
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <input
                  type="checkbox"
                  checked={item.is_paid}
                  onChange={(e) => updateCommitment(index, "is_paid", e.target.checked)}
                />
                This bill has been paid
              </label>

              <button
                type="button"
                onClick={() => setCommitments((current) => current.filter((_, i) => i !== index))}
                style={{ background: "#fff", color: "#b91c1c", border: "1px solid #fecaca", borderRadius: 8, padding: "9px 12px", cursor: "pointer" }}
              >
                Remove bill
              </button>
            </section>
          ))}

          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 18 }}>
            <button
              type="button"
              onClick={() => {
                setCommitments((current) => [...current, emptyCommitment()]);
                setMessage("");
                setFormError("");
              }}
              style={{ background: "#fff", color: "#0f766e", border: "1px solid #0f766e", borderRadius: 8, padding: "11px 15px", fontWeight: 700, cursor: "pointer" }}
            >
              + Add another bill
            </button>

            <button
              type="submit"
              disabled={busy}
              style={{ background: "#0f766e", color: "#fff", border: 0, borderRadius: 8, padding: "11px 18px", fontWeight: 700, cursor: busy ? "wait" : "pointer" }}
            >
              {busy ? "Saving commitments..." : "Save commitments"}
            </button>
          </div>

          {formError && <p role="alert" style={{ color: "#b91c1c" }}>{formError}</p>}
          {message && <p role="status" style={{ color: "#0f766e" }}>{message}</p>}
        </form>
      )}
    </main>
  );
}