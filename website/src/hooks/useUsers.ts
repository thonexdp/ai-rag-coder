import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '../constants/queryKeys';
import { createUser, deleteUser, getUsers, updateUser } from '../services/users.service';

export function useUsers() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.users,
    queryFn: getUsers,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.users });

  return {
    ...query,
    createUser: useMutation({ mutationFn: createUser, onSuccess: invalidate }),
    updateUser: useMutation({
      mutationFn: ({ userId, payload }: { userId: number; payload: Parameters<typeof updateUser>[1] }) =>
        updateUser(userId, payload),
      onSuccess: invalidate,
    }),
    deleteUser: useMutation({ mutationFn: deleteUser, onSuccess: invalidate }),
  };
}
