import { useMemo, useState } from 'react';

import { ScheduleForm } from '../components/forms/ScheduleForm';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { SearchInput } from '../components/ui/SearchInput';
import { Spinner } from '../components/ui/Spinner';
import { Table, type Column } from '../components/ui/Table';
import { useCourses } from '../hooks/useCourses';
import { useSchedules } from '../hooks/useSchedules';
import { useToast } from '../hooks/useToast';
import { useUsers } from '../hooks/useUsers';
import { useUiStore } from '../store/ui.store';
import type { SelectOption } from '../types/api.types';
import type { Schedule, SchedulePayload } from '../types/schedule.types';

export function SchedulesPage() {
  const [search, setSearch] = useState('');
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const schedulesQuery = useSchedules();
  const usersQuery = useUsers();
  const coursesQuery = useCourses();
  const { toast } = useToast();
  const openConfirmDialog = useUiStore((state) => state.openConfirmDialog);

  const filteredSchedules = useMemo(
    () =>
      (schedulesQuery.data ?? []).filter((schedule) =>
        `${schedule.student_name} ${schedule.course_code} ${schedule.weekday}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [schedulesQuery.data, search],
  );

  const studentOptions: SelectOption[] = (usersQuery.data ?? [])
    .filter((user) => user.role === 'student')
    .map((user) => ({ label: `${user.full_name} (${user.email})`, value: String(user.id) }));

  const courseOptions: SelectOption[] = (coursesQuery.data ?? []).map((course) => ({
    label: `${course.code} - ${course.title}`,
    value: String(course.id),
  }));

  const columns: Column<Schedule>[] = [
    { key: 'student', header: 'Student', render: (schedule) => schedule.student_name },
    { key: 'course', header: 'Course', render: (schedule) => `${schedule.course_code} - ${schedule.course_title}` },
    { key: 'weekday', header: 'Weekday', render: (schedule) => schedule.weekday },
    { key: 'time', header: 'Time', render: (schedule) => `${schedule.start_time.slice(0, 5)} - ${schedule.end_time.slice(0, 5)}` },
    { key: 'room', header: 'Room', render: (schedule) => schedule.room ?? '-' },
    {
      key: 'actions',
      header: 'Actions',
      render: (schedule) => (
        <div className="table-actions">
          <Button type="button" variant="outline" onClick={() => (setEditingSchedule(schedule), setIsModalOpen(true))}>
            Edit
          </Button>
          <Button
            type="button"
            variant="danger"
            onClick={() =>
              openConfirmDialog({
                title: 'Delete schedule',
                description: `Delete ${schedule.course_code} for ${schedule.student_name}?`,
                confirmLabel: 'Delete',
                onConfirm: async () => {
                  await schedulesQuery.deleteSchedule.mutateAsync(schedule.id);
                  toast('Schedule deleted.', 'success');
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

  if (schedulesQuery.isLoading || usersQuery.isLoading || coursesQuery.isLoading) {
    return <Spinner />;
  }

  const handleSubmit = async (payload: SchedulePayload) => {
    if (editingSchedule) {
      await schedulesQuery.updateSchedule.mutateAsync({ scheduleId: editingSchedule.id, payload });
      toast('Schedule updated.', 'success');
    } else {
      await schedulesQuery.createSchedule.mutateAsync(payload);
      toast('Schedule assigned.', 'success');
    }
    setEditingSchedule(null);
    setIsModalOpen(false);
  };

  return (
    <section className="page-stack">
      <div className="card">
        <div className="card-header">
          <h2>Student schedules</h2>
          <Button type="button" onClick={() => (setEditingSchedule(null), setIsModalOpen(true))}>
            Assign schedule
          </Button>
        </div>
        <div className="toolbar">
          <SearchInput placeholder="Search by student, course, or weekday" value={search} onChange={setSearch} />
        </div>
        <Table columns={columns} data={filteredSchedules} emptyMessage="No schedules assigned." />
      </div>
      <Modal
        open={isModalOpen}
        title={editingSchedule ? 'Edit schedule' : 'Assign schedule'}
        onClose={() => setIsModalOpen(false)}
      >
        <ScheduleForm
          initialValues={editingSchedule}
          studentOptions={studentOptions}
          courseOptions={courseOptions}
          onSubmit={handleSubmit}
        />
      </Modal>
    </section>
  );
}
