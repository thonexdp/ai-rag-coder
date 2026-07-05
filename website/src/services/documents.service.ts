import { apiClient } from '../lib/apiClient';
import type { DocumentRecord, UploadDocumentPayload } from '../types/document.types';

export async function getDocuments() {
  const { data } = await apiClient.get<DocumentRecord[]>('/documents');
  return data;
}

export async function uploadDocument(payload: UploadDocumentPayload) {
  const formData = new FormData();
  formData.append('title', payload.title);
  formData.append('file', payload.file);
  const { data } = await apiClient.post('/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return data;
}

export async function deleteDocument(documentId: number) {
  await apiClient.delete(`/documents/${documentId}`);
}
