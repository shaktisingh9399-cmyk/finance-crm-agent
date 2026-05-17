/** Global UI state — loading, errors, modals. */

import { create } from "zustand";

interface UiStore {
  isLoading: boolean;
  error: string | null;
  modalOpen: boolean;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setModalOpen: (open: boolean) => void;
}

export const useUiStore = create<UiStore>((set) => ({
  isLoading: false,
  error: null,
  modalOpen: false,
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setModalOpen: (modalOpen) => set({ modalOpen }),
}));
