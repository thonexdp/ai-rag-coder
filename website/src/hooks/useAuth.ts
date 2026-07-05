import { useAuthStore } from '../store/auth.store';

export function useAuth() {
  const token = useAuthStore((state) => state.token);
  const currentUser = useAuthStore((state) => state.currentUser);
  const logout = useAuthStore((state) => state.logout);

  return {
    isAuthenticated: Boolean(token),
    token,
    currentUser,
    logout,
  };
}
