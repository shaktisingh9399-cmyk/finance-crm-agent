/** Application chrome — top navigation and page container. */

import { useAuth } from "@/hooks/useAuth";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 to-slate-50">
      <header className="border-b border-slate-200 bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-bank-navy text-sm font-bold text-bank-gold">
              BI
            </div>
            <div>
              <p className="text-base font-semibold text-bank-navy">BankIQ CRM</p>
              <p className="text-xs text-slate-500">AI assistant for relationship managers</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium text-slate-800">
                  {user.first_name || user.username}
                </p>
                <p className="text-xs text-slate-500">Branch {user.branch_code}</p>
              </div>
            )}
            <button
              type="button"
              onClick={() => logout()}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
