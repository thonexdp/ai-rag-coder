import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '../constants/queryKeys';
import {
  createAnnouncement,
  deleteAnnouncement,
  getAnnouncements,
  updateAnnouncement,
} from '../services/announcements.service';

export function useAnnouncements() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.announcements });

  return {
    ...useQuery({
      queryKey: queryKeys.announcements,
      queryFn: getAnnouncements,
    }),
    createAnnouncement: useMutation({ mutationFn: createAnnouncement, onSuccess: invalidate }),
    updateAnnouncement: useMutation({
      mutationFn: ({
        announcementId,
        payload,
      }: {
        announcementId: number;
        payload: Parameters<typeof updateAnnouncement>[1];
      }) => updateAnnouncement(announcementId, payload),
      onSuccess: invalidate,
    }),
    deleteAnnouncement: useMutation({ mutationFn: deleteAnnouncement, onSuccess: invalidate }),
  };
}
