import 'document_picker_service_stub.dart'
    if (dart.library.html) 'document_picker_service_web.dart';

abstract class DocumentPickerService {
  Future<PickedDocument?> pickDocument();
}

class PickedDocument {
  const PickedDocument({
    required this.filename,
    required this.bytes,
  });

  final String filename;
  final List<int> bytes;
}

DocumentPickerService createDocumentPickerService() => createPickerService();
