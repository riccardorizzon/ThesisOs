import { create } from "zustand";

type UIState = { activeRoute: string; setActiveRoute: (r: string) => void };

export const useUIStore = create<UIState>((set) => ({
  activeRoute: "chat",
  setActiveRoute: (r) => set({ activeRoute: r }),
}));
