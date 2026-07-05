import { Navigate, Route, Routes } from 'react-router-dom';

import { AppShell } from './components/layout/AppShell';
import { AuthGuard } from './components/auth/AuthGuard';
import { ConfirmDialog } from './components/ui/ConfirmDialog';
import { ToastContainer } from './components/ui/ToastContainer';
import { ROUTES } from './constants/routes';
import { AnnouncementsPage } from './pages/AnnouncementsPage';
import { CalendarPage } from './pages/CalendarPage';
import { CoursesPage } from './pages/CoursesPage';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { LoginPage } from './pages/LoginPage';
import { SchedulesPage } from './pages/SchedulesPage';
import { UsersPage } from './pages/UsersPage';

export default function App() {
  return (
    <>
      <Routes>
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route element={<AuthGuard />}>
          <Route element={<AppShell />}>
            <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
            <Route path={ROUTES.USERS} element={<UsersPage />} />
            <Route path={ROUTES.COURSES} element={<CoursesPage />} />
            <Route path={ROUTES.SCHEDULES} element={<SchedulesPage />} />
            <Route path={ROUTES.ANNOUNCEMENTS} element={<AnnouncementsPage />} />
            <Route path={ROUTES.CALENDAR} element={<CalendarPage />} />
            <Route path={ROUTES.DOCUMENTS} element={<DocumentsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      </Routes>
      <ConfirmDialog />
      <ToastContainer />
    </>
  );
}
