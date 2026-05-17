/** Auth hook — login, refresh, logout via authStore. */

import { useAuthStore } from "@/store/authStore";

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const accessToken = useAuthStore((s) => s.accessToken);
  const login = useAuthStore((s) => s.login);
  const logout = useAuthStore((s) => s.logout);
  const refreshAccessToken = useAuthStore((s) => s.refreshAccessToken);

  return {
    user,
    isAuthenticated: Boolean(accessToken),
    login,
    logout,
    refreshAccessToken,
  };
}
