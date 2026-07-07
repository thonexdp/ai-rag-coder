import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

/// Supported app languages for TTS and STT.
enum AppLanguage { english, tagalog, bisaya }

/// Result returned by [VoiceService.speak] so the caller
/// knows whether audio was actually played or silently skipped.
enum SpeakResult { played, skippedNoVoice }

class VoiceService {
  VoiceService({stt.SpeechToText? speechToText, FlutterTts? flutterTts})
    : _stt = speechToText ?? stt.SpeechToText(),
      _tts = flutterTts ?? FlutterTts();

  final stt.SpeechToText _stt;
  final FlutterTts _tts;

  bool _sttInitialized = false;
  bool _isSpeaking = false;
  bool _isListening = false;

  bool get isSpeaking => _isSpeaking;
  bool get isListening => _isListening;

  // ── Languages that have an actual TTS voice ──────────────────────────────
  // Bisaya/Cebuano is intentionally excluded — no engine supports ceb-PH.
  // Callers should hide the voice button when language is [AppLanguage.bisaya].
  static const Map<AppLanguage, String> _ttsLocales = {
    AppLanguage.english: 'en-US',
    AppLanguage.tagalog: 'fil-PH',
    // bisaya → omitted on purpose
  };

  // ── STT locales — what the mic listens for ───────────────────────────────
  // Bisaya falls back to fil-PH (closest available, still imperfect).
  static const Map<AppLanguage, String> _sttLocales = {
    AppLanguage.english: 'en-US',
    AppLanguage.tagalog: 'fil-PH',
    AppLanguage.bisaya: 'fil-PH', // best available fallback for STT
  };

  // ── Whether a language has a real TTS voice ──────────────────────────────
  bool canSpeak(AppLanguage language) => _ttsLocales.containsKey(language);

  // ── Initialize STT once ──────────────────────────────────────────────────
  Future<bool> _ensureSttInitialized() async {
    if (_sttInitialized) return true;
    _sttInitialized = await _stt.initialize(
      onError: (_) => _isListening = false,
    );
    return _sttInitialized;
  }

  // ── Configure TTS once ───────────────────────────────────────────────────
  Future<void> _configureTts() async {
    await _tts.setSpeechRate(
      0.45,
    ); // slightly slower — better for school context
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
    _tts.setCompletionHandler(() => _isSpeaking = false);
    _tts.setErrorHandler((_) => _isSpeaking = false);
  }

  // ── STT: start listening ─────────────────────────────────────────────────
  /// [language] sets the locale the microphone listens for.
  /// [onPartialResult] fires on intermediate speech recognition results.
  /// [onFinalResult] fires once when speech recognition reaches a final result.
  Future<void> startListening({
    void Function(String text)? onPartialResult,
    void Function(String text)? onFinalResult,
    void Function()? onUnavailable,
    void Function()? onDone,
    AppLanguage language = AppLanguage.english,
  }) async {
    final ready = await _ensureSttInitialized();
    if (!ready) {
      onUnavailable?.call();
      return;
    }
    if (_isListening) return;

    _isListening = true;
    await _stt.listen(
      onResult: (result) {
        if (result.recognizedWords.isNotEmpty) {
          onPartialResult?.call(result.recognizedWords);
          if (result.finalResult) {
            _isListening = false;
            onFinalResult?.call(result.recognizedWords);
            onDone?.call();
          }
        }
      },
      localeId: _sttLocales[language],
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 4), // auto-stops after 4s silence
      cancelOnError: true,
      onSoundLevelChange: (_) {},
    );
  }

  // ── STT: stop listening ──────────────────────────────────────────────────
  Future<void> stopListening() async {
    _isListening = false;
    await _stt.stop();
  }

  // ── TTS: speak ───────────────────────────────────────────────────────────
  /// Returns [SpeakResult.skippedNoVoice] for Bisaya so the UI can
  /// show a tooltip instead of silently doing nothing.
  Future<SpeakResult> speak(
    String text, {
    AppLanguage language = AppLanguage.english,
  }) async {
    // Bisaya — no TTS engine supports it, skip gracefully
    if (!canSpeak(language)) return SpeakResult.skippedNoVoice;

    // Stop any ongoing speech before starting new one
    if (_isSpeaking) await stop();

    await _configureTts();
    await _tts.setLanguage(_ttsLocales[language]!);

    _isSpeaking = true;
    await _tts.speak(text);

    return SpeakResult.played;
  }

  // ── TTS: stop ────────────────────────────────────────────────────────────
  Future<void> stop() async {
    _isSpeaking = false;
    await _tts.stop();
  }

  // ── Cleanup ──────────────────────────────────────────────────────────────
  Future<void> dispose() async {
    await stopListening();
    await stop();
  }
}
