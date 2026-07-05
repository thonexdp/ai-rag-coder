import { useMemo, useState } from 'react';

import { UserForm } from '../components/forms/UserForm';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { SearchInput } from '../components/ui/SearchInput';
import { Spinner } from '../components/ui/Spinner';
import { Table, type Column } from '../components/ui/Table';
import { useUsers } from '../hooks/useUsers';
import { useToast } from '../hooks/useToast';
import { useUiStore } from '../store/ui.store';
import type { CreateUserPayload, UpdateUserPayload, User } from '../types/user.types';

export function UsersPage() {
  const [search, setSearch] = useState('');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const usersQuery = useUsers();
  const { toast } = useToast();
  const openConfirmDialog = useUiStore((state) => state.openConfirmDialog);

  const filteredUsers = useMemo(
    () =>
      (usersQuery.data ?? []).filter((user) =>
        `${user.full_name} ${user.email}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [search, usersQuery.data],
  );

  const columns: Column<User>[] = [
    { key: 'name', header: 'Full name', render: (user) => user.full_name },
    { key: 'email', header: 'Email', render: (user) => user.email },
    { key: 'role', header: 'Role', render: (user) => <Badge tone={user.role}>{user.role}</Badge> },
    { key: 'joined', header: 'Joined', render: (user) => new Date(user.created_at).toLocaleDateString() },
    {
      key: 'actions',
      header: 'Actions',
      render: (user) => (
        <div className="table-actions">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setEditingUser(user);
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
                title: 'Delete user',
                description: `Delete ${user.full_name}?`,
                confirmLabel: 'Delete',
                onConfirm: async () => {
                  await usersQuery.deleteUser.mutateAsync(user.id);
                  toast('User deleted.', 'success');
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

  if (usersQuery.isLoading) {
    return <Spinner />;
  }

  const handleSubmit = async (payload: CreateUserPayload | UpdateUserPayload) => {
    if (editingUser) {
      await usersQuery.updateUser.mutateAsync({ userId: editingUser.id, payload: payload as UpdateUserPayload });
      toast('User updated.', 'success');
    } else {
      await usersQuery.createUser.mutateAsync(payload as CreateUserPayload);
      toast('User created.', 'success');
    }
    setEditingUser(null);
    setIsModalOpen(false);
  };

  return (
    <section className="page-stack">
      <div className="card">
        <div className="card-header">
          <h2>All users</h2>
          <Button
            type="button"
            onClick={() => {
              setEditingUser(null);
              setIsModalOpen(true);
            }}
          >
            Add user
          </Button>
        </div>
        <div className="toolbar">
          <SearchInput placeholder="Search by name or email" value={search} onChange={setSearch} />
        </div>
        <Table columns={columns} data={filteredUsers} emptyMessage="No users found." />
      </div>
      <Modal
        open={isModalOpen}
        title={editingUser ? 'Edit user' : 'Add user'}
        onClose={() => {
          setEditingUser(null);
          setIsModalOpen(false);
        }}
        footer={null}
      >
        <UserForm initialValues={editingUser} onSubmit={handleSubmit} />
      </Modal>
    </section>
  );
}
