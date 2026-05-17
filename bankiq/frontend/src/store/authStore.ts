/** JWT auth state — tokens held in memory only, never localStorage. */

import { create } from "zustand";

import { api } from "@/lib/api";
import type { RelationshipManager, TokenPair } from "@/types/api";

interface AuthState {
  user: RelationshipManager | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,

  login: async (username: string, password: string) => {
    const { data } = await api.post<TokenPair>("/auth/token/", { username, password });
    set({ accessToken: data.access, refreshToken: data.refresh });
    const profile = await api.get<RelationshipManager>("/accounts/rms/");
    const user = Array.isArray(profile.data)
      ? (profile.data as RelationshipManager[])[0]
      : profile.data;
    set({ user: user ?? null });
  },

  logout: () => {
    set({ user: null, accessToken: null, refreshToken: null });
  },

  refreshAccessToken: async () => {
    const refresh = get().refreshToken;
    if (!refresh) return false;
    try {
      const { data } = await api.post<{ access: string }>("/auth/token/refresh/", {
        refresh,
      });
      set({ accessToken: data.access });
      return true;
    } catch {
      get().logout();
      return false;
    }
  },
}));
