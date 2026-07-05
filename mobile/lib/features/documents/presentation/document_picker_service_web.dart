import 'dart:async';
import 'dart:html' as html;

import 'document_picker_service.dart';

class WebDocumentPickerService implements DocumentPickerService {
  @override
  Future<PickedDocument?> pickDocument() async {
    final input = html.FileUploadInputElement()
      ..accept = '.pdf,.docx,.txt'
      ..multiple = false;

    final completer = Completer<PickedDocument?>();

    input.onChange.listen((_) {
      final file = input.files?.first;
      if (file == null) {
        if (!completer.isCompleted) {
          completer.complete(null);
        }
        return;
      }

      final reader = html.FileReader();
      reader.onLoadEnd.listen((_) {
        final result = reader.result;
        if (result is! List<int>) {
          if (!completer.isCompleted) {
            completer.complete(null);
          }
          return;
        }
        if (!completer.isCompleted) {
          completer.complete(PickedDocument(filename: file.name, bytes: result));
        }
      });
      reader.onError.listen((_) {
        if (!completer.isCompleted) {
          completer.complete(null);
        }
      });
      reader.readAsArrayBuffer(file);
    });

    input.click();
    return completer.future;
  }
}

DocumentPickerService createPickerService() => WebDocumentPickerService();
