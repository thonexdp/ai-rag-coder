import { useMemo, useState } from 'react';

import { CalendarEventForm } from '../components/forms/CalendarEventForm';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { SearchInput } from '../components/ui/SearchInput';
import { Spinner } from '../components/ui/Spinner';
import { Table, type Column } from '../components/ui/Table';
import { useCalendarEvents } from '../hooks/useCalendarEvents';
import { useToast } from '../hooks/useToast';
import { useUiStore } from '../store/ui.store';
import type { CalendarEvent, CalendarEventPayload } from '../types/calendar.types';

export function CalendarPage() {
  const [search, setSearch] = useState('');
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const calendarQuery = useCalendarEvents();
  const { toast } = useToast();
  const openConfirmDialog = useUiStore((state) => state.openConfirmDialog);

  const filteredEvents = useMemo(
    () =>
      (calendarQuery.data ?? []).filter((event) =>
        `${event.title} ${event.description ?? ''}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [calendarQuery.data, search],
  );

  const columns: Column<CalendarEvent>[] = [
    { key: 'title', header: 'Title', render: (event) => event.title },
    { key: 'description', header: 'Description', render: (event) => event.description ?? 'No description' },
    { key: 'date', header: 'Event date', render: (event) => event.event_date },
    {
      key: 'actions',
      header: 'Actions',
      render: (event) => (
        <div className="table-actions">
          <Button type="button" variant="outline" onClick={() => (setEditingEvent(event), setIsModalOpen(true))}>
            Edit
          </Button>
          <Button
            type="button"
            variant="danger"
            onClick={() =>
              openConfirmDialog({
                title: 'Delete event',
                description: `Delete "${event.title}"?`,
                confirmLabel: 'Delete',
                onConfirm: async () => {
                  await calendarQuery.deleteCalendarEvent.mutateAsync(event.id);
                  toast('Event deleted.', 'success');
                },
              })
            }
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  if (calendarQuery.isLoading) {
    return <Spinner />;
  }

  const handleSubmit = async (payload: CalendarEventPayload) => {
    if (editingEvent) {
      await calendarQuery.updateCalendarEvent.mutateAsync({ eventId: editingEvent.id, payload });
      toast('Event updated.', 'success');
    } else {
      await calendarQuery.createCalendarEvent.mutateAsync(payload);
      toast('Event added.', 'success');
    }
    setEditingEvent(null);
    setIsModalOpen(false);
  };

  return (
    <section className="page-stack">
      <div className="card">
        <div className="card-header">
          <h2>School calendar</h2>
          <Button type="button" onClick={() => (setEditingEvent(null), setIsModalOpen(true))}>
            Add event
          </Button>
        </div>
        <div className="toolbar">
          <SearchInput placeholder="Search events" value={search} onChange={setSearch} />
        </div>
        <Table columns={columns} data={filteredEvents} emptyMessage="No calendar events yet." />
      </div>
      <Modal open={isModalOpen} title={editingEvent ? 'Edit event' : 'Add event'} onClose={() => setIsModalOpen(false)}>
        <CalendarEventForm initialValues={editingEvent} onSubmit={handleSubmit} />
      </Modal>
    </section>
  );
}
