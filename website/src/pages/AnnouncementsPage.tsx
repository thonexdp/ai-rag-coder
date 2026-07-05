import { useMemo, useState } from 'react';

import { AnnouncementForm } from '../components/forms/AnnouncementForm';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { SearchInput } from '../components/ui/SearchInput';
import { Spinner } from '../components/ui/Spinner';
import { Table, type Column } from '../components/ui/Table';
import { useAnnouncements } from '../hooks/useAnnouncements';
import { useToast } from '../hooks/useToast';
import { useUiStore } from '../store/ui.store';
import type { Announcement, AnnouncementPayload } from '../types/announcement.types';

export function AnnouncementsPage() {
  const [search, setSearch] = useState('');
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const announcementsQuery = useAnnouncements();
  const { toast } = useToast();
  const openConfirmDialog = useUiStore((state) => state.openConfirmDialog);

  const filteredAnnouncements = useMemo(
    () =>
      (announcementsQuery.data ?? []).filter((announcement) =>
        `${announcement.title} ${announcement.content}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [announcementsQuery.data, search],
  );

  const columns: Column<Announcement>[] = [
    { key: 'title', header: 'Title', render: (announcement) => announcement.title },
    { key: 'content', header: 'Content', render: (announcement) => announcement.content },
    {
      key: 'published',
      header: 'Published',
      render: (announcement) => new Date(announcement.published_at).toLocaleString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (announcement) => (
        <div className="table-actions">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setEditingAnnouncement(announcement);
              setIsModalOpen(true);
            }}
          >
            Edit
          </Button>
          <Button
            type="button"
            variant="danger"
            onClick={() =>
              openConfirmDialog({
                title: 'Delete announcement',
                description: `Delete "${announcement.title}"?`,
                confirmLabel: 'Delete',
                onConfirm: async () => {
                  await announcementsQuery.deleteAnnouncement.mutateAsync(announcement.id);
                  toast('Announcement deleted.', 'success');
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

  if (announcementsQuery.isLoading) {
    return <Spinner />;
  }

  const handleSubmit = async (payload: AnnouncementPayload) => {
    if (editingAnnouncement) {
      await announcementsQuery.updateAnnouncement.mutateAsync({
        announcementId: editingAnnouncement.id,
        payload,
      });
      toast('Announcement updated.', 'success');
    } else {
      await announcementsQuery.createAnnouncement.mutateAsync(payload);
      toast('Announcement published.', 'success');
    }
    setEditingAnnouncement(null);
    setIsModalOpen(false);
  };

  return (
    <section className="page-stack">
      <div className="card">
        <div className="card-header">
          <h2>Announcements</h2>
          <Button type="button" onClick={() => (setEditingAnnouncement(null), setIsModalOpen(true))}>
            New announcement
          </Button>
        </div>
        <div className="toolbar">
          <SearchInput placeholder="Search announcements" value={search} onChange={setSearch} />
        </div>
        <Table columns={columns} data={filteredAnnouncements} emptyMessage="No announcements available." />
      </div>
      <Modal
        open={isModalOpen}
        title={editingAnnouncement ? 'Edit announcement' : 'New announcement'}
        onClose={() => setIsModalOpen(false)}
      >
        <AnnouncementForm initialValues={editingAnnouncement} onSubmit={handleSubmit} />
      </Modal>
    </section>
  );
}
