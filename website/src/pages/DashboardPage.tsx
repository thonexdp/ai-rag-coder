import { useAnnouncements } from '../hooks/useAnnouncements';
import { useCalendarEvents } from '../hooks/useCalendarEvents';
import { useCourses } from '../hooks/useCourses';
import { useDocuments } from '../hooks/useDocuments';
import { useUsers } from '../hooks/useUsers';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { StatCard } from '../components/ui/StatCard';

export function DashboardPage() {
  const users = useUsers();
  const courses = useCourses();
  const announcements = useAnnouncements();
  const documents = useDocuments();
  const calendar = useCalendarEvents();

  if ([users, courses, announcements, documents, calendar].some((query) => query.isLoading)) {
    return <Spinner />;
  }

  return (
    <section className="page-stack">
      <div className="stats-row">
        <StatCard label="Users" value={users.data?.length ?? 0} />
        <StatCard label="Courses" value={courses.data?.length ?? 0} />
        <StatCard label="Announcements" value={announcements.data?.length ?? 0} />
        <StatCard label="Documents" value={documents.data?.length ?? 0} />
      </div>
      <div className="dash-grid">
        <div className="card panel-body">
          <div className="card-header">
            <h2>Recent announcements</h2>
          </div>
          <div className="panel-list">
            {announcements.data?.length ? (
              announcements.data.slice(0, 4).map((announcement) => (
                <article key={announcement.id} className="list-item">
                  <strong>{announcement.title}</strong>
                  <p>{announcement.content}</p>
                </article>
              ))
            ) : (
              <EmptyState title="No announcements yet" description="Create one from the announcements page." />
            )}
          </div>
        </div>
        <div className="card panel-body">
          <div className="card-header">
            <h2>Upcoming calendar events</h2>
          </div>
          <div className="panel-list">
            {calendar.data?.length ? (
              calendar.data.slice(0, 4).map((event) => (
                <article key={event.id} className="list-item">
                  <strong>{event.title}</strong>
                  <p>{event.event_date}</p>
                </article>
              ))
            ) : (
              <EmptyState title="No calendar events yet" description="Add one from the calendar page." />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
