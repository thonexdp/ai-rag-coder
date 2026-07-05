export type UserRole = 'admin' | 'faculty' | 'student';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface CreateUserPayload {
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
}

export interface UpdateUserPayload {
  email: string;
  full_name: string;
  password?: string;
  role: UserRole;
}
