import { apiClient } from '../lib/apiClient';
import type { Announcement, AnnouncementPayload } from '../types/announcement.types';

export async function getAnnouncements() {
  const { data } = await apiClient.get<Announcement[]>('/announcements');
  return data;
}

export async function createAnnouncement(payload: AnnouncementPayload) {
  const { data } = await apiClient.post<Announcement>('/announcements', payload);
  return data;
}

export async function updateAnnouncement(announcementId: number, payload: AnnouncementPayload) {
  const { data } = await apiClient.put<Announcement>(`/announcements/${announcementId}`, payload);
  return data;
}

export async function deleteAnnouncement(announcementId: number) {
  await apiClient.delete(`/announcements/${announcementId}`);
}
