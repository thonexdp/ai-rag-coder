import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '../ui/Button';
import type { CalendarEvent, CalendarEventPayload } from '../../types/calendar.types';

const schema = z.object({
  title: z.string().min(2),
  description: z.string().optional(),
  event_date: z.string().min(4),
});

type FormValues = z.infer<typeof schema>;

interface CalendarEventFormProps {
  initialValues?: CalendarEvent | null;
  onSubmit: (data: CalendarEventPayload) => void;
}

export function CalendarEventForm({ initialValues, onSubmit }: CalendarEventFormProps) {
  const { handleSubmit, register, reset } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: initialValues?.title ?? '',
      description: initialValues?.description ?? '',
      event_date: initialValues?.event_date ?? '',
    },
  });

  useEffect(() => {
    reset({
      title: initialValues?.title ?? '',
      description: initialValues?.description ?? '',
      event_date: initialValues?.event_date ?? '',
    });
  }, [initialValues, reset]);

  return (
    <form className="form-stack" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <label className="form-row">
        <span>Title</span>
        <input {...register('title')} />
      </label>
      <label className="form-row">
        <span>Description</span>
        <textarea {...register('description')} rows={4} />
      </label>
      <label className="form-row">
        <span>Event date</span>
        <input {...register('event_date')} type="date" />
      </label>
      <Button type="submit">{initialValues ? 'Save changes' : 'Add event'}</Button>
    </form>
  );
}
