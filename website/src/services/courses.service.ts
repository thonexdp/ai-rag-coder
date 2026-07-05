import { apiClient } from '../lib/apiClient';
import type { Course, CoursePayload } from '../types/course.types';

export async function getCourses() {
  const { data } = await apiClient.get<Course[]>('/courses');
  return data;
}

export async function createCourse(payload: CoursePayload) {
  const { data } = await apiClient.post<Course>('/courses', payload);
  return data;
}

export async function updateCourse(courseId: number, payload: CoursePayload) {
  const { data } = await apiClient.put<Course>(`/courses/${courseId}`, payload);
  return data;
}

export async function deleteCourse(courseId: number) {
  await apiClient.delete(`/courses/${courseId}`);
}
