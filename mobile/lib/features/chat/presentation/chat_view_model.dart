import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/services/voice_service.dart';
import '../../auth/presentation/auth_view_model.dart';
import '../../settings/presentation/settings_view_model.dart';
import '../data/chat_repository.dart';
import '../domain/chat_models.dart';

const _unsetSessionId = Object();

final voiceServiceProvider = Provider<VoiceService>((ref) {
  return VoiceService();
});

final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  return ChatRepository(ref.read(apiClientProvider));
});

class ChatState {
  const ChatState({
    this.messages = const [],
    this.sessions = const [],
    this.sessionId,
    this.isSending = false,
    this.isListening = false,
    this.error,
    this.language = AppLanguage.english,
    this.voiceDraft = '',
  });

  final List<ChatMessageItem> messages;
  final List<ChatSessionItem> sessions;
  final int? sessionId;
  final bool isSending;
  final bool isListening;
  final String? error;
  final AppLanguage language;
  final String voiceDraft;

  ChatState copyWith({
    List<ChatMessageItem>? messages,
    List<ChatSessionItem>? sessions,
    Object? sessionId = _unsetSessionId,
    bool? isSending,
    bool? isListening,
    String? error,
    bool clearError = false,
    AppLanguage? language,
    String? voiceDraft,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      sessions: sessions ?? this.sessions,
      sessionId: identical(sessionId, _unsetSessionId) ? this.sessionId : sessionId as int?,
      isSending: isSending ?? this.isSending,
      isListening: isListening ?? this.isListening,
      error: clearError ? null : error ?? this.error,
      language: language ?? this.language,
      voiceDraft: voiceDraft ?? this.voiceDraft,
    );
  }
}

class ChatViewModel extends StateNotifier<ChatState> {
  ChatViewModel(this._ref, this._repository, this._voiceService) : super(const ChatState()) {
    loadHistory();
  }

  final Ref _ref;
  final ChatRepository _repository;
  final VoiceService _voiceService;
  bool _voiceAutoSubmitInFlight = false;
  static const _voiceCorrectionPreviewDelay = Duration(milliseconds: 300);

  Future<void> loadHistory() async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    try {
      final sessions = await _repository.getHistory(token);
      state = state.copyWith(sessions: sessions, clearError: true);
    } catch (error) {
      state = state.copyWith(error: error.toString());
    }
  }

  Future<void> sendMessage(String text) async {
    final authState = _ref.read(authViewModelProvider);
    if (authState.token == null || text.trim().isEmpty) {
      return;
    }

    final outbound = ChatMessageItem(role: 'user', content: text.trim());
    state = state.copyWith(
      messages: [...state.messages, outbound],
      isSending: true,
      clearError: true,
    );

    try {
      final result = await _repository.sendMessage(
        token: authState.token!,
        message: text.trim(),
        sessionId: state.sessionId,
        language: _languageCode(state.language),
      );
      state = state.copyWith(
        messages: [...state.messages, result.$1],
        sessionId: result.$2,
        language: _languageFromCode(result.$3),
        isSending: false,
      );
      if (_ref.read(settingsViewModelProvider).enableTextToSpeech) {
        await _voiceService.speak(
          result.$1.content,
          language: _languageFromCode(result.$3),
        );
      }
      await loadHistory();
    } catch (error) {
      state = state.copyWith(isSending: false, error: error.toString());
    }
  }

  Future<void> loadSession(int sessionId) async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    try {
      final messages = await _repository.getSession(token, sessionId);
      state = state.copyWith(messages: messages, sessionId: sessionId, clearError: true);
    } catch (error) {
      state = state.copyWith(error: error.toString());
    }
  }

  Future<void> startVoiceInput(void Function(String text) onRecognized) async {
    if (state.isSending || state.isListening) {
      return;
    }
    _voiceAutoSubmitInFlight = false;
    state = state.copyWith(isListening: true, clearError: true, voiceDraft: '');
    await _voiceService.startListening(
      onPartialResult: (text) {
        state = state.copyWith(voiceDraft: text);
        onRecognized(text);
      },
      onFinalResult: (text) async {
        state = state.copyWith(isListening: false, voiceDraft: text);
        onRecognized(text);
        await submitVoiceDraft();
      },
      onUnavailable: () {
        state = state.copyWith(
          isListening: false,
          error: 'Voice input is unavailable on this device or browser.',
        );
      },
      onDone: () {
        if (state.isListening) {
          state = state.copyWith(isListening: false);
        }
      },
      language: state.language,
    );
  }

  Future<void> stopVoiceInput() async {
    await _voiceService.stopListening();
    state = state.copyWith(isListening: false);
    await submitVoiceDraft();
  }

  void startNewChat() {
    state = state.copyWith(
      messages: const [],
      sessionId: null,
      clearError: true,
    );
  }

  Future<void> deleteSession(int sessionId) async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    try {
      await _repository.deleteSession(token, sessionId);
      final shouldResetCurrent = state.sessionId == sessionId;
      state = state.copyWith(
        messages: shouldResetCurrent ? const [] : null,
        sessionId: shouldResetCurrent ? null : _unsetSessionId,
        clearError: true,
      );
      await loadHistory();
    } catch (error) {
      state = state.copyWith(error: error.toString());
    }
  }

  Future<void> deleteAllHistory() async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    try {
      await _repository.deleteAllHistory(token);
      state = state.copyWith(
        sessions: const [],
        messages: const [],
        sessionId: null,
        clearError: true,
      );
    } catch (error) {
      state = state.copyWith(error: error.toString());
    }
  }

  void setLanguage(AppLanguage value) {
    state = state.copyWith(language: value);
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }

  Future<void> submitVoiceDraft() async {
    if (_voiceAutoSubmitInFlight || state.isSending) {
      return;
    }
    final originalText = state.voiceDraft.trim();
    if (originalText.isEmpty) {
      state = state.copyWith(
        error: 'No voice input detected. Please try again.',
        voiceDraft: '',
      );
      return;
    }

    _voiceAutoSubmitInFlight = true;
    try {
      final correctedText = await _correctVoiceTranscript(originalText);
      state = state.copyWith(voiceDraft: correctedText, clearError: true);
      await Future<void>.delayed(_voiceCorrectionPreviewDelay);
      state = state.copyWith(voiceDraft: '');
      await sendMessage(correctedText);
    } finally {
      _voiceAutoSubmitInFlight = false;
    }
  }

  Future<String> _correctVoiceTranscript(String transcript) async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return transcript;
    }

    final language = _languageCode(state.language);
    if (!_shouldCorrectVoiceTranscript(language)) {
      return transcript;
    }

    try {
      final corrected = await _repository.correctTranscript(
        token: token,
        transcript: transcript,
        language: language,
      );
      return corrected.trim().isEmpty ? transcript : corrected.trim();
    } catch (_) {
      return transcript;
    }
  }

  bool _shouldCorrectVoiceTranscript(String language) {
    return language == 'fil' || language == 'ceb';
  }

  String _languageCode(AppLanguage language) {
    switch (language) {
      case AppLanguage.tagalog:
        return 'fil';
      case AppLanguage.bisaya:
        return 'ceb';
      case AppLanguage.english:
        return 'en';
    }
  }

  AppLanguage _languageFromCode(String code) {
    switch (code.toLowerCase()) {
      case 'fil':
      case 'tl':
      case 'tagalog':
        return AppLanguage.tagalog;
      case 'ceb':
      case 'bisaya':
      case 'cebuano':
        return AppLanguage.bisaya;
      default:
        return AppLanguage.english;
    }
  }
}

final chatViewModelProvider = StateNotifierProvider<ChatViewModel, ChatState>((ref) {
  return ChatViewModel(
    ref,
    ref.read(chatRepositoryProvider),
    ref.read(voiceServiceProvider),
  );
});
