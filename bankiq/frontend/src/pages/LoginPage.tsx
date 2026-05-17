/** RM login — clear labels and demo account hint for local development. */

import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useUiStore } from "@/store/uiStore";

export function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const { setError, setLoading, isLoading, error } = useUiStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("We could not sign you in. Check your username and password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hidden flex-1 flex-col justify-between bg-bank-navy p-10 text-white lg:flex">
        <div>
          <p className="text-2xl font-bold text-bank-gold">BankIQ CRM</p>
          <p className="mt-1 text-sm text-slate-300">Built for relationship managers</p>
        </div>
        <div className="max-w-md space-y-4">
          <h2 className="text-3xl font-semibold leading-snug">
            Find the right customers. Stay compliant. Reach out with confidence.
          </h2>
          <p className="text-sm leading-relaxed text-slate-300">
            BankIQ helps you identify high-potential customers in your portfolio, runs regulatory
            checks automatically, and drafts personalised WhatsApp messages — without exposing
            sensitive data.
          </p>
        </div>
        <p className="text-xs text-slate-500">RBI / TRAI compliance enforced on every campaign</p>
      </div>

      <div className="flex flex-1 items-center justify-center bg-slate-50 p-6">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-lg"
        >
          <h1 className="text-xl font-bold text-bank-navy">Sign in to your workspace</h1>
          <p className="mt-1 text-sm text-slate-500">
            Use your relationship manager credentials
          </p>

          {error && (
            <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
              {error}
            </p>
          )}

          <div className="mt-6 space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-700">
                Username
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-bank-gold focus:outline-none focus:ring-2 focus:ring-bank-gold/20"
                required
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-bank-gold focus:outline-none focus:ring-2 focus:ring-bank-gold/20"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="mt-6 w-full rounded-lg bg-bank-navy py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {isLoading ? "Signing in…" : "Continue to workspace"}
          </button>

          <div className="mt-6 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 text-xs text-slate-600">
            <p className="font-medium text-slate-700">Demo account (local dev)</p>
            <p className="mt-1">
              Username: <code className="rounded bg-white px-1">rm_demo</code> · Password:{" "}
              <code className="rounded bg-white px-1">demo1234</code>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
