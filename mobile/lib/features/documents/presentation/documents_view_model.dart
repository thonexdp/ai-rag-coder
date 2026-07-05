import 'dart:async';
import 'dart:typed_data';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/presentation/auth_view_model.dart';
import '../data/documents_repository.dart';
import '../domain/document_item.dart';
import 'document_picker_service.dart';

final documentsRepositoryProvider = Provider<DocumentsRepository>((ref) {
  return DocumentsRepository(ref.read(apiClientProvider));
});

final documentPickerServiceProvider = Provider<DocumentPickerService>((ref) {
  return createDocumentPickerService();
});

class DocumentsState {
  const DocumentsState({
    this.documents = const [],
    this.isLoading = false,
    this.processingPollCount = 0,
    this.error,
  });

  final List<DocumentItem> documents;
  final bool isLoading;
  final int processingPollCount;
  final String? error;

  DocumentsState copyWith({
    List<DocumentItem>? documents,
    bool? isLoading,
    int? processingPollCount,
    String? error,
    bool clearError = false,
  }) {
    return DocumentsState(
      documents: documents ?? this.documents,
      isLoading: isLoading ?? this.isLoading,
      processingPollCount: processingPollCount ?? this.processingPollCount,
      error: clearError ? null : error ?? this.error,
    );
  }
}

class DocumentsViewModel extends StateNotifier<DocumentsState> {
  DocumentsViewModel(this._ref, this._repository, this._documentPickerService) : super(const DocumentsState()) {
    loadDocuments();
  }

  final Ref _ref;
  final DocumentsRepository _repository;
  final DocumentPickerService _documentPickerService;
  Timer? _pollingTimer;

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> loadDocuments() async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final documents = await _repository.listDocuments(token);
      state = state.copyWith(documents: documents, isLoading: false);
      _syncPolling(documents);
    } catch (error) {
      state = state.copyWith(isLoading: false, error: error.toString());
    }
  }

  Future<void> pickAndUploadDocument() async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }

    final pickedDocument = await _documentPickerService.pickDocument();
    if (pickedDocument == null) {
      state = state.copyWith(
        error: 'No file selected, or file upload is not supported on this platform.',
      );
      return;
    }

    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _repository.uploadDocument(
        token: token,
        bytes: Uint8List.fromList(pickedDocument.bytes),
        filename: pickedDocument.filename,
        title: pickedDocument.filename,
      );
      await loadDocuments();
    } catch (error) {
      state = state.copyWith(isLoading: false, error: error.toString());
    }
  }

  Future<void> deleteDocument(int documentId) async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    await _repository.deleteDocument(token: token, documentId: documentId);
    await loadDocuments();
  }

  void _syncPolling(List<DocumentItem> documents) {
    final shouldPoll = documents.any(
      (document) => document.status == 'pending' || document.status == 'processing',
    );

    if (!shouldPoll) {
      _pollingTimer?.cancel();
      _pollingTimer = null;
      state = state.copyWith(processingPollCount: 0);
      return;
    }

    state = state.copyWith(processingPollCount: state.processingPollCount + 1);

    if (_pollingTimer != null) {
      return;
    }

    _pollingTimer = Timer.periodic(const Duration(seconds: 3), (_) {
      loadDocuments();
    });
  }
}

final documentsViewModelProvider = StateNotifierProvider<DocumentsViewModel, DocumentsState>((ref) {
  return DocumentsViewModel(
    ref,
    ref.read(documentsRepositoryProvider),
    ref.read(documentPickerServiceProvider),
  );
});
