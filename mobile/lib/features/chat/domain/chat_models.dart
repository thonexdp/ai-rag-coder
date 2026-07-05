class ChatSource {
  const ChatSource({
    required this.title,
    required this.snippet,
    this.documentId,
    this.page,
    this.sourceType = 'document',
  });

  final int? documentId;
  final String title;
  final String snippet;
  final int? page;
  final String sourceType;

  factory ChatSource.fromJson(Map<String, dynamic> json) {
    return ChatSource(
      documentId: json['document_id'] as int?,
      title: json['title'] as String? ?? 'Source',
      snippet: json['snippet'] as String? ?? '',
      page: json['page'] as int?,
      sourceType: json['source_type'] as String? ?? 'document',
    );
  }
}

class ChatMessageItem {
  const ChatMessageItem({
    required this.role,
    required this.content,
    this.sources = const [],
  });

  final String role;
  final String content;
  final List<ChatSource> sources;
}

class ChatSessionItem {
  const ChatSessionItem({
    required this.id,
    required this.title,
  });

  final int id;
  final String title;

  factory ChatSessionItem.fromJson(Map<String, dynamic> json) {
    return ChatSessionItem(
      id: json['id'] as int,
      title: json['title'] as String? ?? 'Chat',
    );
  }
}
