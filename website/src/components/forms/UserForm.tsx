import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { ROLES } from '../../constants/roles';
import { Button } from '../ui/Button';
import type { CreateUserPayload, UpdateUserPayload, User } from '../../types/user.types';

const schema = z.object({
  email: z.string().email(),
  full_name: z.string().min(2),
  password: z.string().min(8).optional().or(z.literal('')),
  role: z.enum([ROLES.ADMIN, ROLES.FACULTY, ROLES.STUDENT]),
});

type FormValues = z.infer<typeof schema>;

interface UserFormProps {
  initialValues?: User | null;
  onSubmit: (data: CreateUserPayload | UpdateUserPayload) => void;
}

export function UserForm({ initialValues, onSubmit }: UserFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: initialValues?.email ?? '',
      full_name: initialValues?.full_name ?? '',
      password: '',
      role: initialValues?.role ?? ROLES.STUDENT,
    },
  });

  useEffect(() => {
    reset({
      email: initialValues?.email ?? '',
      full_name: initialValues?.full_name ?? '',
      password: '',
      role: initialValues?.role ?? ROLES.STUDENT,
    });
  }, [initialValues, reset]);

  return (
    <form
      className="form-stack"
      onSubmit={handleSubmit((values) =>
        onSubmit({
          email: values.email,
          full_name: values.full_name,
          role: values.role,
          ...(values.password ? { password: values.password } : {}),
        } as CreateUserPayload | UpdateUserPayload),
      )}
    >
      <label className="form-row">
        <span>Email</span>
        <input {...register('email')} type="email" />
        <small>{errors.email?.message}</small>
      </label>
      <label className="form-row">
        <span>Full name</span>
        <input {...register('full_name')} />
        <small>{errors.full_name?.message}</small>
      </label>
      <label className="form-row">
        <span>Password {initialValues ? '(optional)' : ''}</span>
        <input {...register('password')} type="password" />
        <small>{errors.password?.message}</small>
      </label>
      <label className="form-row">
        <span>Role</span>
        <select {...register('role')}>
          <option value={ROLES.ADMIN}>Admin</option>
          <option value={ROLES.FACULTY}>Faculty</option>
          <option value={ROLES.STUDENT}>Student</option>
        </select>
      </label>
      <Button type="submit">{initialValues ? 'Save changes' : 'Create user'}</Button>
    </form>
  );
}
