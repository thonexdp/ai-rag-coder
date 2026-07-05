import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '../constants/queryKeys';
import {
  createCalendarEvent,
  deleteCalendarEvent,
  getCalendarEvents,
  updateCalendarEvent,
} from '../services/calendar.service';

export function useCalendarEvents() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.calendarEvents });

  return {
    ...useQuery({
      queryKey: queryKeys.calendarEvents,
      queryFn: getCalendarEvents,
    }),
    createCalendarEvent: useMutation({ mutationFn: createCalendarEvent, onSuccess: invalidate }),
    updateCalendarEvent: useMutation({
      mutationFn: ({
        eventId,
        payload,
      }: {
        eventId: number;
        payload: Parameters<typeof updateCalendarEvent>[1];
      }) => updateCalendarEvent(eventId, payload),
      onSuccess: invalidate,
    }),
    deleteCalendarEvent: useMutation({ mutationFn: deleteCalendarEvent, onSuccess: invalidate }),
  };
}
