import { useMemo, useState } from 'react';

import { CourseForm } from '../components/forms/CourseForm';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { SearchInput } from '../components/ui/SearchInput';
import { Spinner } from '../components/ui/Spinner';
import { Table, type Column } from '../components/ui/Table';
import { useCourses } from '../hooks/useCourses';
import { useToast } from '../hooks/useToast';
import { useUiStore } from '../store/ui.store';
import type { Course, CoursePayload } from '../types/course.types';

export function CoursesPage() {
  const [search, setSearch] = useState('');
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const coursesQuery = useCourses();
  const { toast } = useToast();
  const openConfirmDialog = useUiStore((state) => state.openConfirmDialog);

  const filteredCourses = useMemo(
    () =>
      (coursesQuery.data ?? []).filter((course) =>
        `${course.code} ${course.title}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [coursesQuery.data, search],
  );

  const columns: Column<Course>[] = [
    { key: 'code', header: 'Code', render: (course) => course.code },
    { key: 'title', header: 'Title', render: (course) => course.title },
    { key: 'description', header: 'Description', render: (course) => course.description ?? 'No description' },
    {
      key: 'actions',
      header: 'Actions',
      render: (course) => (
        <div className="table-actions">
          <Button type="button" variant="outline" onClick={() => (setEditingCourse(course), setIsModalOpen(true))}>
            Edit
          </Button>
          <Button
            type="button"
            variant="danger"
            onClick={() =>
              openConfirmDialog({
                title: 'Delete course',
                description: `Delete ${course.code}?`,
                confirmLabel: 'Delete',
                onConfirm: async () => {
                  await coursesQuery.deleteCourse.mutateAsync(course.id);
                  toast('Course deleted.', 'success');
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

  if (coursesQuery.isLoading) {
    return <Spinner />;
  }

  const handleSubmit = async (payload: CoursePayload) => {
    if (editingCourse) {
      await coursesQuery.updateCourse.mutateAsync({ courseId: editingCourse.id, payload });
      toast('Course updated.', 'success');
    } else {
      await coursesQuery.createCourse.mutateAsync(payload);
      toast('Course created.', 'success');
    }
    setEditingCourse(null);
    setIsModalOpen(false);
  };

  return (
    <section className="page-stack">
      <div className="card">
        <div className="card-header">
          <h2>Courses</h2>
          <Button type="button" onClick={() => (setEditingCourse(null), setIsModalOpen(true))}>
            Add course
          </Button>
        </div>
        <div className="toolbar">
          <SearchInput placeholder="Search by code or title" value={search} onChange={setSearch} />
        </div>
        <Table columns={columns} data={filteredCourses} emptyMessage="No courses found." />
      </div>
      <Modal open={isModalOpen} title={editingCourse ? 'Edit course' : 'Add course'} onClose={() => setIsModalOpen(false)}>
        <CourseForm initialValues={editingCourse} onSubmit={handleSubmit} />
      </Modal>
    </section>
  );
}
