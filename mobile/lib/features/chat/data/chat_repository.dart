import '../../../core/services/api_client.dart';
import '../domain/chat_models.dart';

class ChatRepository {
  ChatRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<(ChatMessageItem, int, String)> sendMessage({
    required String token,
    required String message,
    int? sessionId,
    String? language,
  }) async {
    final response = await _apiClient.postJson(
      '/chat',
      token: token,
      body: {
        'message': message,
        'session_id': sessionId,
        'language': language,
      },
    );

    final sources = ((response['sources'] as List<dynamic>? ?? <dynamic>[]))
        .map((source) => ChatSource.fromJson(source as Map<String, dynamic>))
        .toList();

    return (
      ChatMessageItem(
        role: 'assistant',
        content: response['answer'] as String,
        sources: sources,
      ),
      response['session_id'] as int,
      response['language'] as String? ?? 'en',
    );
  }

  Future<List<ChatSessionItem>> getHistory(String token) async {
    final response = await _apiClient.getJsonList('/chat/history', token: token);
    return response
        .map((item) => ChatSessionItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<ChatMessageItem>> getSession(String token, int sessionId) async {
    final response = await _apiClient.getJson('/chat/history/$sessionId', token: token);
    final messages = response['messages'] as List<dynamic>? ?? <dynamic>[];
    return messages.map((item) {
      final json = item as Map<String, dynamic>;
      final citations = (json['citations'] as List<dynamic>? ?? <dynamic>[])
          .map((source) => ChatSource.fromJson(source as Map<String, dynamic>))
          .toList();
      return ChatMessageItem(
        role: json['role'] as String? ?? 'assistant',
        content: json['content'] as String? ?? '',
        sources: citations,
      );
    }).toList();
  }

  Future<void> deleteSession(String token, int sessionId) {
    return _apiClient.delete('/chat/history/$sessionId', token: token);
  }

  Future<void> deleteAllHistory(String token) {
    return _apiClient.delete('/chat/history', token: token);
  }
}
