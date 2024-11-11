import { create } from "zustand";

type UserState = {
  user: {
    // TODO: This will eventually carry more user information (name, avatar, etc.)
    email: string;
  } | null;
};

type UserActions = {
  setUser: (user: UserState["user"]) => void;
  logout: () => void;
};

export const useUserStore = create<UserState & UserActions>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
