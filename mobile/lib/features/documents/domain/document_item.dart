class DocumentItem {
  const DocumentItem({
    required this.id,
    required this.title,
    required this.filename,
    required this.status,
    this.failureReason,
  });

  final int id;
  final String title;
  final String filename;
  final String status;
  final String? failureReason;

  factory DocumentItem.fromJson(Map<String, dynamic> json) {
    return DocumentItem(
      id: json['id'] as int,
      title: json['title'] as String? ?? 'Untitled',
      filename: json['filename'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      failureReason: json['failure_reason'] as String?,
    );
  }
}
