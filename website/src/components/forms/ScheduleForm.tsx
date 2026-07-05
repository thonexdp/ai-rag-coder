import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '../ui/Button';
import type { SelectOption } from '../../types/api.types';
import type { Schedule, SchedulePayload } from '../../types/schedule.types';

const schema = z.object({
  student_id: z.coerce.number().int().positive(),
  course_id: z.coerce.number().int().positive(),
  weekday: z.string().min(2),
  start_time: z.string().min(4),
  end_time: z.string().min(4),
  room: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface ScheduleFormProps {
  initialValues?: Schedule | null;
  studentOptions: SelectOption[];
  courseOptions: SelectOption[];
  onSubmit: (data: SchedulePayload) => void;
}

export function ScheduleForm({ courseOptions, initialValues, onSubmit, studentOptions }: ScheduleFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      student_id: initialValues?.student_id ?? 0,
      course_id: initialValues?.course_id ?? 0,
      weekday: initialValues?.weekday ?? '',
      start_time: initialValues?.start_time?.slice(0, 5) ?? '',
      end_time: initialValues?.end_time?.slice(0, 5) ?? '',
      room: initialValues?.room ?? '',
    },
  });

  useEffect(() => {
    reset({
      student_id: initialValues?.student_id ?? 0,
      course_id: initialValues?.course_id ?? 0,
      weekday: initialValues?.weekday ?? '',
      start_time: initialValues?.start_time?.slice(0, 5) ?? '',
      end_time: initialValues?.end_time?.slice(0, 5) ?? '',
      room: initialValues?.room ?? '',
    });
  }, [initialValues, reset]);

  return (
    <form
      className="form-stack"
      onSubmit={handleSubmit((values) =>
        onSubmit({
          ...values,
          start_time: `${values.start_time}:00`,
          end_time: `${values.end_time}:00`,
        }),
      )}
    >
      <label className="form-row">
        <span>Student</span>
        <select {...register('student_id')}>
          <option value={0}>Select student</option>
          {studentOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <small>{errors.student_id?.message}</small>
      </label>
      <label className="form-row">
        <span>Course</span>
        <select {...register('course_id')}>
          <option value={0}>Select course</option>
          {courseOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <small>{errors.course_id?.message}</small>
      </label>
      <div className="form-cols">
        <label className="form-row">
          <span>Weekday</span>
          <input {...register('weekday')} />
        </label>
        <label className="form-row">
          <span>Room</span>
          <input {...register('room')} />
        </label>
      </div>
      <div className="form-cols">
        <label className="form-row">
          <span>Start time</span>
          <input {...register('start_time')} type="time" />
        </label>
        <label className="form-row">
          <span>End time</span>
          <input {...register('end_time')} type="time" />
        </label>
      </div>
      <small>{errors.weekday?.message ?? errors.start_time?.message ?? errors.end_time?.message}</small>
      <Button type="submit">{initialValues ? 'Save changes' : 'Assign schedule'}</Button>
    </form>
  );
}
