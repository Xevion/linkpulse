import { create } from "zustand";

type UserState = {
  initialized: boolean;
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
  initialized: false,
  user: null,
  setUser: (user) => set({ user, initialized: true }),
  logout: () => set({ user: null }),
}));
