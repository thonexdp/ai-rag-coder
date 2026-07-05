export interface Schedule {
  id: number;
  student_id: number;
  course_id: number;
  weekday: string;
  start_time: string;
  end_time: string;
  room: string | null;
  student_name: string;
  student_email: string;
  course_code: string;
  course_title: string;
}

export interface SchedulePayload {
  student_id: number;
  course_id: number;
  weekday: string;
  start_time: string;
  end_time: string;
  room?: string;
}
