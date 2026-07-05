import { apiClient } from '../lib/apiClient';
import type { LoginPayload, LoginResponse, User } from '../types/user.types';

export async function login(payload: LoginPayload) {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', payload);
  return data;
}

export async function getMe() {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
}
