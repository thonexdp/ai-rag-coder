import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/services/secure_storage_service.dart';
import '../../auth/presentation/auth_view_model.dart';

class SettingsState {
  const SettingsState({
    this.showChatSources = true,
    this.showChatSourceSnippets = true,
    this.enableTextToSpeech = true,
    this.isLoading = true,
  });

  final bool showChatSources;
  final bool showChatSourceSnippets;
  final bool enableTextToSpeech;
  final bool isLoading;

  SettingsState copyWith({
    bool? showChatSources,
    bool? showChatSourceSnippets,
    bool? enableTextToSpeech,
    bool? isLoading,
  }) {
    return SettingsState(
      showChatSources: showChatSources ?? this.showChatSources,
      showChatSourceSnippets: showChatSourceSnippets ?? this.showChatSourceSnippets,
      enableTextToSpeech: enableTextToSpeech ?? this.enableTextToSpeech,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class SettingsViewModel extends StateNotifier<SettingsState> {
  SettingsViewModel(this._storage) : super(const SettingsState()) {
    load();
  }

  final SecureStorageService _storage;

  Future<void> load() async {
    final showChatSources = await _storage.readShowChatSources();
    final showChatSourceSnippets = await _storage.readShowChatSourceSnippets();
    final enableTextToSpeech = await _storage.readEnableTextToSpeech();
    state = state.copyWith(
      showChatSources: showChatSources,
      showChatSourceSnippets: showChatSourceSnippets,
      enableTextToSpeech: enableTextToSpeech,
      isLoading: false,
    );
  }

  Future<void> setShowChatSources(bool value) async {
    await _storage.saveShowChatSources(value);
    state = state.copyWith(showChatSources: value);
  }

  Future<void> setShowChatSourceSnippets(bool value) async {
    await _storage.saveShowChatSourceSnippets(value);
    state = state.copyWith(showChatSourceSnippets: value);
  }

  Future<void> setEnableTextToSpeech(bool value) async {
    await _storage.saveEnableTextToSpeech(value);
    state = state.copyWith(enableTextToSpeech: value);
  }
}

final settingsViewModelProvider = StateNotifierProvider<SettingsViewModel, SettingsState>((ref) {
  return SettingsViewModel(ref.read(secureStorageProvider));
});
