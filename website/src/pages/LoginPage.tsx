import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { ROUTES } from '../constants/routes';
import { useAuth } from '../hooks/useAuth';
import { useLogin } from '../hooks/useLogin';
import { useToast } from '../hooks/useToast';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const loginMutation = useLogin();
  const { toast } = useToast();
  const { handleSubmit, register } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: 'admin@school.local',
      password: 'Admin123!',
    },
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate(ROUTES.DASHBOARD, { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="login-screen open">
      <div className="login-card">
        <div className="logo">
          <div className="login-logo-icon">SA</div>
          <h1>School Assistant</h1>
          <p>Admin Panel sign in to continue</p>
        </div>
        <form
          className="form-stack"
          onSubmit={handleSubmit(async (values) => {
            try {
              await loginMutation.mutateAsync(values);
              navigate(ROUTES.DASHBOARD, { replace: true });
            } catch (error) {
              toast(error instanceof Error ? error.message : 'Login failed', 'error');
            }
          })}
        >
          <label className="form-row">
            <span>Email</span>
            <input {...register('email')} type="email" />
          </label>
          <label className="form-row">
            <span>Password</span>
            <input {...register('password')} type="password" />
          </label>
          <button className="btn btn-primary" type="submit" disabled={loginMutation.isPending}>
            {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}
