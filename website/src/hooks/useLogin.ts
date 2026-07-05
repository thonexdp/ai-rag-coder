import { useMutation } from '@tanstack/react-query';

import { login } from '../services/auth.service';
import { useAuthStore } from '../store/auth.store';

export function useLogin() {
  const setAuth = useAuthStore((state) => state.setAuth);

  return useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
    },
  });
}
