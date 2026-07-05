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
    this.language = 'en',
  });

  final List<ChatMessageItem> messages;
  final List<ChatSessionItem> sessions;
  final int? sessionId;
  final bool isSending;
  final bool isListening;
  final String? error;
  final String language;

  ChatState copyWith({
    List<ChatMessageItem>? messages,
    List<ChatSessionItem>? sessions,
    Object? sessionId = _unsetSessionId,
    bool? isSending,
    bool? isListening,
    String? error,
    bool clearError = false,
    String? language,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      sessions: sessions ?? this.sessions,
      sessionId: identical(sessionId, _unsetSessionId) ? this.sessionId : sessionId as int?,
      isSending: isSending ?? this.isSending,
      isListening: isListening ?? this.isListening,
      error: clearError ? null : error ?? this.error,
      language: language ?? this.language,
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
        language: state.language,
      );
      state = state.copyWith(
        messages: [...state.messages, result.$1],
        sessionId: result.$2,
        language: result.$3,
        isSending: false,
      );
      if (_ref.read(settingsViewModelProvider).enableTextToSpeech) {
        await _voiceService.speak(result.$1.content, language: result.$3);
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
    state = state.copyWith(isListening: true, clearError: true);
    await _voiceService.startListening((text) {
      onRecognized(text);
    });
  }

  Future<void> stopVoiceInput() async {
    await _voiceService.stopListening();
    state = state.copyWith(isListening: false);
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

  void setLanguage(String value) {
    state = state.copyWith(language: value);
  }
}

final chatViewModelProvider = StateNotifierProvider<ChatViewModel, ChatState>((ref) {
  return ChatViewModel(
    ref,
    ref.read(chatRepositoryProvider),
    ref.read(voiceServiceProvider),
  );
});
