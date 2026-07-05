import { useState } from 'react';

import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { SearchInput } from '../components/ui/SearchInput';
import { Spinner } from '../components/ui/Spinner';
import { Table, type Column } from '../components/ui/Table';
import { useDocuments } from '../hooks/useDocuments';
import { useToast } from '../hooks/useToast';
import { useUiStore } from '../store/ui.store';
import type { DocumentRecord } from '../types/document.types';

export function DocumentsPage() {
  const [title, setTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [search, setSearch] = useState('');
  const documentsQuery = useDocuments();
  const { toast } = useToast();
  const openConfirmDialog = useUiStore((state) => state.openConfirmDialog);

  if (documentsQuery.isLoading) {
    return <Spinner />;
  }

  const filteredDocuments = (documentsQuery.data ?? []).filter((document) =>
    `${document.title} ${document.filename}`.toLowerCase().includes(search.toLowerCase()),
  );

  const columns: Column<DocumentRecord>[] = [
    { key: 'title', header: 'Title', render: (document) => document.title },
    { key: 'file', header: 'Filename', render: (document) => document.filename },
    { key: 'type', header: 'Type', render: (document) => document.mime_type },
    { key: 'status', header: 'Status', render: (document) => <Badge tone={document.status === 'ready' ? 'success' : 'warning'}>{document.status}</Badge> },
    { key: 'created', header: 'Created', render: (document) => new Date(document.created_at).toLocaleDateString() },
    {
      key: 'actions',
      header: 'Actions',
      render: (document) => (
        <Button
          type="button"
          variant="danger"
          onClick={() =>
            openConfirmDialog({
              title: 'Delete document',
              description: `Delete "${document.title}"?`,
              confirmLabel: 'Delete',
              onConfirm: async () => {
                await documentsQuery.deleteDocument.mutateAsync(document.id);
                toast('Document deleted.', 'success');
              },
            })
          }
        >
          Delete
        </Button>
      ),
    },
  ];

  return (
    <section className="page-stack">
      <div className="card panel-body">
        <div className="card-header">
          <h2>Upload document</h2>
        </div>
        <div className="upload-grid">
          <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Document title" />
          <input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <Button
            type="button"
            disabled={!file || !title || documentsQuery.uploadDocument.isPending}
            onClick={async () => {
              if (!file) {
                return;
              }
              await documentsQuery.uploadDocument.mutateAsync({ title, file });
              setTitle('');
              setFile(null);
              toast('Document uploaded.', 'success');
            }}
          >
            {documentsQuery.uploadDocument.isPending ? 'Uploading...' : 'Upload'}
          </Button>
        </div>
      </div>
      <div className="card">
        <div className="card-header">
          <h2>Documents</h2>
        </div>
        <div className="toolbar">
          <SearchInput placeholder="Search documents" value={search} onChange={setSearch} />
        </div>
        <Table columns={columns} data={filteredDocuments} emptyMessage="No documents uploaded yet." />
      </div>
    </section>
  );
}
