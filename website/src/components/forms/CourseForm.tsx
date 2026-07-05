import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '../ui/Button';
import type { Course, CoursePayload } from '../../types/course.types';

const schema = z.object({
  code: z.string().min(2),
  title: z.string().min(2),
  description: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface CourseFormProps {
  initialValues?: Course | null;
  onSubmit: (data: CoursePayload) => void;
}

export function CourseForm({ initialValues, onSubmit }: CourseFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      code: initialValues?.code ?? '',
      title: initialValues?.title ?? '',
      description: initialValues?.description ?? '',
    },
  });

  useEffect(() => {
    reset({
      code: initialValues?.code ?? '',
      title: initialValues?.title ?? '',
      description: initialValues?.description ?? '',
    });
  }, [initialValues, reset]);

  return (
    <form className="form-stack" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <label className="form-row">
        <span>Code</span>
        <input {...register('code')} />
        <small>{errors.code?.message}</small>
      </label>
      <label className="form-row">
        <span>Title</span>
        <input {...register('title')} />
        <small>{errors.title?.message}</small>
      </label>
      <label className="form-row">
        <span>Description</span>
        <textarea {...register('description')} rows={4} />
      </label>
      <Button type="submit">{initialValues ? 'Save changes' : 'Create course'}</Button>
    </form>
  );
}
