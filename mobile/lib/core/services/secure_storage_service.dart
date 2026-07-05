import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  SecureStorageService() : _storage = const FlutterSecureStorage();

  final FlutterSecureStorage _storage;
  static const _tokenKey = 'auth_token';
  static const _showChatSourcesKey = 'show_chat_sources';
  static const _showChatSourceSnippetsKey = 'show_chat_source_snippets';
  static const _enableTextToSpeechKey = 'enable_text_to_speech';

  Future<void> saveToken(String token) => _storage.write(key: _tokenKey, value: token);

  Future<String?> readToken() => _storage.read(key: _tokenKey);

  Future<void> clearToken() => _storage.delete(key: _tokenKey);

  Future<void> saveShowChatSources(bool value) =>
      _storage.write(key: _showChatSourcesKey, value: value.toString());

  Future<bool> readShowChatSources() async {
    final value = await _storage.read(key: _showChatSourcesKey);
    return value == null ? true : value.toLowerCase() == 'true';
  }

  Future<void> saveShowChatSourceSnippets(bool value) =>
      _storage.write(key: _showChatSourceSnippetsKey, value: value.toString());

  Future<bool> readShowChatSourceSnippets() async {
    final value = await _storage.read(key: _showChatSourceSnippetsKey);
    return value == null ? true : value.toLowerCase() == 'true';
  }

  Future<void> saveEnableTextToSpeech(bool value) =>
      _storage.write(key: _enableTextToSpeechKey, value: value.toString());

  Future<bool> readEnableTextToSpeech() async {
    final value = await _storage.read(key: _enableTextToSpeechKey);
    return value == null ? true : value.toLowerCase() == 'true';
  }
}
