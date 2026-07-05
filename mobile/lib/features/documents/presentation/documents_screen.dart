import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'documents_view_model.dart';

class DocumentsScreen extends ConsumerWidget {
  const DocumentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(documentsViewModelProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Documents'),
        actions: [
          IconButton(
            onPressed: () => ref.read(documentsViewModelProvider.notifier).loadDocuments(),
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            onPressed: () => ref.read(documentsViewModelProvider.notifier).pickAndUploadDocument(),
            icon: const Icon(Icons.upload_file),
          ),
        ],
      ),
      body: state.isLoading && state.documents.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (state.error != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(state.error!, style: const TextStyle(color: Colors.red)),
                  ),
                if (state.processingPollCount >= 20)
                  const Padding(
                    padding: EdgeInsets.only(bottom: 12),
                    child: Text(
                      'A document is still processing. If this lasts more than a minute, check the backend logs for embedding or upload errors.',
                    ),
                  ),
                ...state.documents.map(
                  (document) => Card(
                    child: ListTile(
                      title: Text(document.title),
                      subtitle: Text(
                        document.failureReason == null || document.failureReason!.isEmpty
                            ? '${document.filename}\nStatus: ${document.status}'
                            : '${document.filename}\nStatus: ${document.status}\nError: ${document.failureReason}',
                      ),
                      isThreeLine: true,
                      trailing: IconButton(
                        icon: const Icon(Icons.delete_outline),
                        onPressed: () => ref
                            .read(documentsViewModelProvider.notifier)
                            .deleteDocument(document.id),
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}
