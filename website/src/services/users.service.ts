import { apiClient } from '../lib/apiClient';
import type { CreateUserPayload, UpdateUserPayload, User } from '../types/user.types';

export async function getUsers() {
  const { data } = await apiClient.get<User[]>('/users');
  return data;
}

export async function createUser(payload: CreateUserPayload) {
  const { data } = await apiClient.post<User>('/users', payload);
  return data;
}

export async function updateUser(userId: number, payload: UpdateUserPayload) {
  const { data } = await apiClient.put<User>(`/users/${userId}`, payload);
  return data;
}

export async function deleteUser(userId: number) {
  await apiClient.delete(`/users/${userId}`);
}
