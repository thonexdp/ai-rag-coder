import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { User } from '../types/user.types';

interface AuthState {
  token: string | null;
  currentUser: User | null;
  setAuth: (token: string, currentUser: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      currentUser: null,
      setAuth: (token, currentUser) => set({ token, currentUser }),
      logout: () => set({ token: null, currentUser: null }),
    }),
    {
      name: 'school-admin-auth',
      partialize: (state) => ({ token: state.token, currentUser: state.currentUser }),
    },
  ),
);
