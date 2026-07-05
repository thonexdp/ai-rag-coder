import { apiClient } from '../lib/apiClient';
import type { Schedule, SchedulePayload } from '../types/schedule.types';

export async function getSchedules() {
  const { data } = await apiClient.get<Schedule[]>('/schedules');
  return data;
}

export async function createSchedule(payload: SchedulePayload) {
  const { data } = await apiClient.post<Schedule>('/schedules', payload);
  return data;
}

export async function updateSchedule(scheduleId: number, payload: SchedulePayload) {
  const { data } = await apiClient.put<Schedule>(`/schedules/${scheduleId}`, payload);
  return data;
}

export async function deleteSchedule(scheduleId: number) {
  await apiClient.delete(`/schedules/${scheduleId}`);
}
