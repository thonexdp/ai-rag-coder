import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { ROUTES } from '../../constants/routes';
import { useAuth } from '../../hooks/useAuth';

export function AuthGuard() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace state={{ from: location }} />;
  }

  return <Outlet />;
}
