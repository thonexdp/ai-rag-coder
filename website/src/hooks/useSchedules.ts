import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '../constants/queryKeys';
import { createSchedule, deleteSchedule, getSchedules, updateSchedule } from '../services/schedules.service';

export function useSchedules() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.schedules });

  return {
    ...useQuery({
      queryKey: queryKeys.schedules,
      queryFn: getSchedules,
    }),
    createSchedule: useMutation({ mutationFn: createSchedule, onSuccess: invalidate }),
    updateSchedule: useMutation({
      mutationFn: ({ scheduleId, payload }: { scheduleId: number; payload: Parameters<typeof updateSchedule>[1] }) =>
        updateSchedule(scheduleId, payload),
      onSuccess: invalidate,
    }),
    deleteSchedule: useMutation({ mutationFn: deleteSchedule, onSuccess: invalidate }),
  };
}
