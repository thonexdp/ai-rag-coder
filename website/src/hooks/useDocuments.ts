import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '../constants/queryKeys';
import { deleteDocument, getDocuments, uploadDocument } from '../services/documents.service';

export function useDocuments() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.documents });

  return {
    ...useQuery({
      queryKey: queryKeys.documents,
      queryFn: getDocuments,
      refetchInterval: 10000,
    }),
    uploadDocument: useMutation({ mutationFn: uploadDocument, onSuccess: invalidate }),
    deleteDocument: useMutation({ mutationFn: deleteDocument, onSuccess: invalidate }),
  };
}
