import { useLocation } from 'react-router-dom';

import { ROUTES } from '../../constants/routes';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/Button';

const topbarMeta: Record<string, { title: string; sub: string }> = {
  [ROUTES.DASHBOARD]: { title: 'Dashboard', sub: 'Overview of all records' },
  [ROUTES.USERS]: { title: 'Users', sub: 'Manage students, faculty and admin accounts' },
  [ROUTES.COURSES]: { title: 'Courses', sub: 'Add and manage course catalogue' },
  [ROUTES.SCHEDULES]: { title: 'Student Schedules', sub: 'Assign courses and time slots to students' },
  [ROUTES.ANNOUNCEMENTS]: { title: 'Announcements', sub: 'Post updates visible in the mobile app' },
  [ROUTES.CALENDAR]: { title: 'School Calendar', sub: 'Key academic dates and events' },
  [ROUTES.DOCUMENTS]: { title: 'RAG Documents', sub: 'View and manage uploaded documents for AI search' },
};

export function Topbar() {
  const location = useLocation();
  const { logout } = useAuth();
  const meta = topbarMeta[location.pathname] ?? topbarMeta[ROUTES.DASHBOARD];

  return (
    <div className="topbar">
      <div>
        <div className="topbar-title">{meta.title}</div>
        <div className="topbar-sub">{meta.sub}</div>
      </div>
      <Button type="button" variant="outline" onClick={logout}>
        Sign out
      </Button>
    </div>
  );
}
