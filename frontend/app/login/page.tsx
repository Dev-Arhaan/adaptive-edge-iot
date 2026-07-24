"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function LoginPage() {
  const [passphrase, setPassphrase] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    try {
      const { token } = await api.login(passphrase);
      window.localStorage.setItem("dashboard_token", token);
      router.push("/dashboard");
    } catch {
      setError("Incorrect passphrase.");
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleSubmit} className="w-80 rounded-lg border border-panel-border bg-panel p-8">
        <h1 className="mb-1 font-display text-xl tracking-tight text-bone">Fire Watch</h1>
        <p className="mb-6 text-sm text-muted">Adaptive Edge-IoT Simulation Console</p>
        <input
          type="password" value={passphrase} onChange={(e) => setPassphrase(e.target.value)}
          placeholder="Operator passphrase"
          className="mb-3 w-full rounded border border-panel-border bg-void px-3 py-2 font-data text-sm text-bone outline-none focus:border-signal"
        />
        {error && <p className="mb-3 text-sm text-risk-high">{error}</p>}
        <button type="submit" className="w-full rounded bg-signal py-2 font-display text-sm font-medium text-void transition hover:opacity-90">
          Enter station
        </button>
      </form>
    </main>
  );
}