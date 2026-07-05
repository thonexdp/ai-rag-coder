export interface Course {
  id: number;
  code: string;
  title: string;
  description: string | null;
}

export interface CoursePayload {
  code: string;
  title: string;
  description?: string;
}
