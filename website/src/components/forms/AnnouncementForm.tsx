import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '../ui/Button';
import type { Announcement, AnnouncementPayload } from '../../types/announcement.types';

const schema = z.object({
  title: z.string().min(2),
  content: z.string().min(2),
  published_at: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface AnnouncementFormProps {
  initialValues?: Announcement | null;
  onSubmit: (data: AnnouncementPayload) => void;
}

export function AnnouncementForm({ initialValues, onSubmit }: AnnouncementFormProps) {
  const { handleSubmit, register, reset } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: initialValues?.title ?? '',
      content: initialValues?.content ?? '',
      published_at: initialValues?.published_at?.slice(0, 16) ?? '',
    },
  });

  useEffect(() => {
    reset({
      title: initialValues?.title ?? '',
      content: initialValues?.content ?? '',
      published_at: initialValues?.published_at?.slice(0, 16) ?? '',
    });
  }, [initialValues, reset]);

  return (
    <form className="form-stack" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <label className="form-row">
        <span>Title</span>
        <input {...register('title')} />
      </label>
      <label className="form-row">
        <span>Content</span>
        <textarea {...register('content')} rows={5} />
      </label>
      <label className="form-row">
        <span>Publish at</span>
        <input {...register('published_at')} type="datetime-local" />
      </label>
      <Button type="submit">{initialValues ? 'Save changes' : 'Publish announcement'}</Button>
    </form>
  );
}
