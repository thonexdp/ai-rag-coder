import 'dart:typed_data';

import '../../../core/services/api_client.dart';
import '../domain/document_item.dart';

class DocumentsRepository {
  DocumentsRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<List<DocumentItem>> listDocuments(String token) async {
    final response = await _apiClient.getJsonList('/documents', token: token);
    return response
        .map((item) => DocumentItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> uploadDocument({
    required String token,
    required Uint8List bytes,
    required String filename,
    required String title,
  }) async {
    await _apiClient.postMultipart(
      '/documents',
      token: token,
      fieldName: 'file',
      bytes: bytes,
      filename: filename,
      fields: {'title': title},
    );
  }

  Future<void> deleteDocument({
    required String token,
    required int documentId,
  }) {
    return _apiClient.delete('/documents/$documentId', token: token);
  }
}
