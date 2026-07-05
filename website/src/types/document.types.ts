export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'failed';

export interface DocumentRecord {
  id: number;
  title: string;
  filename: string;
  mime_type: string;
  status: DocumentStatus;
  failure_reason: string | null;
  created_at: string;
}

export interface UploadDocumentPayload {
  title: string;
  file: File;
}
