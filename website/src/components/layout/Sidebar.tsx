import { ROUTES } from '../../constants/routes';
import { useAuth } from '../../hooks/useAuth';
import { SidebarItem } from './SidebarItem';

export function Sidebar() {
  const { currentUser } = useAuth();

  return (
    <aside id="sidebar">
      <div className="sb-brand">
        <h1>School Assistant</h1>
        <p>Admin Panel</p>
      </div>
      <nav className="sb-nav">
        <div className="sb-section-label">Overview</div>
        <SidebarItem to={ROUTES.DASHBOARD} label="Dashboard" end />
        <div className="sb-section-label">Users & Academics</div>
        <SidebarItem to={ROUTES.USERS} label="Users" />
        <SidebarItem to={ROUTES.COURSES} label="Courses" />
        <SidebarItem to={ROUTES.SCHEDULES} label="Student Schedules" />
        <div className="sb-section-label">Content</div>
        <SidebarItem to={ROUTES.ANNOUNCEMENTS} label="Announcements" />
        <SidebarItem to={ROUTES.CALENDAR} label="School Calendar" />
        <div className="sb-section-label">RAG Documents</div>
        <SidebarItem to={ROUTES.DOCUMENTS} label="Documents" />
      </nav>
      <div className="sb-bottom">
        <div className="sb-user">
          <div className="sb-avatar">{currentUser?.full_name.slice(0, 2).toUpperCase() ?? 'AD'}</div>
          <div className="sb-user-info">
            <p>{currentUser?.full_name ?? 'Admin'}</p>
            <span>{currentUser?.role ?? 'admin'}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
