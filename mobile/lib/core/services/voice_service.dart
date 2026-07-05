import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';

class VoiceService {
  VoiceService({
    SpeechToText? speechToText,
    FlutterTts? flutterTts,
  })  : _speechToText = speechToText ?? SpeechToText(),
        _flutterTts = flutterTts ?? FlutterTts();

  final SpeechToText _speechToText;
  final FlutterTts _flutterTts;

  Future<bool> initialize() => _speechToText.initialize();

  Future<void> startListening(void Function(String text) onResult) async {
    final isReady = await initialize();
    if (!isReady) {
      return;
    }
    await _speechToText.listen(
      onResult: (result) => onResult(result.recognizedWords),
    );
  }

  Future<void> stopListening() => _speechToText.stop();

  Future<void> speak(String text, {String language = 'en'}) async {
    await _flutterTts.setLanguage(_mapLanguage(language));
    await _flutterTts.speak(text);
  }

  String _mapLanguage(String language) {
    switch (language) {
      case 'fil':
        return 'fil-PH';
      case 'ceb':
        return 'en-PH';
      default:
        return 'en-US';
    }
  }
}
