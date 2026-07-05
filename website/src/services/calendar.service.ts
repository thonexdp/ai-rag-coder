import { apiClient } from '../lib/apiClient';
import type { CalendarEvent, CalendarEventPayload } from '../types/calendar.types';

export async function getCalendarEvents() {
  const { data } = await apiClient.get<CalendarEvent[]>('/calendar');
  return data;
}

export async function createCalendarEvent(payload: CalendarEventPayload) {
  const { data } = await apiClient.post<CalendarEvent>('/calendar', payload);
  return data;
}

export async function updateCalendarEvent(eventId: number, payload: CalendarEventPayload) {
  const { data } = await apiClient.put<CalendarEvent>(`/calendar/${eventId}`, payload);
  return data;
}

export async function deleteCalendarEvent(eventId: number) {
  await apiClient.delete(`/calendar/${eventId}`);
}
