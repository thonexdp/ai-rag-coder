import 'document_picker_service.dart';

class UnsupportedDocumentPickerService implements DocumentPickerService {
  @override
  Future<PickedDocument?> pickDocument() async => null;
}

DocumentPickerService createPickerService() => UnsupportedDocumentPickerService();
