import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/services/api_client.dart';
import '../../../core/services/secure_storage_service.dart';
import '../data/auth_repository.dart';
import '../domain/auth_user.dart';

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.read(apiClientProvider), ref.read(secureStorageProvider));
});

class AuthState {
  const AuthState({
    this.user,
    this.token,
    this.isLoading = false,
    this.error,
    this.isInitialized = false,
  });

  final AuthUser? user;
  final String? token;
  final bool isLoading;
  final String? error;
  final bool isInitialized;

  bool get isAuthenticated => token != null && user != null;

  AuthState copyWith({
    AuthUser? user,
    String? token,
    bool? isLoading,
    String? error,
    bool clearError = false,
    bool? isInitialized,
  }) {
    return AuthState(
      user: user ?? this.user,
      token: token ?? this.token,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : error ?? this.error,
      isInitialized: isInitialized ?? this.isInitialized,
    );
  }
}

class AuthViewModel extends StateNotifier<AuthState> {
  AuthViewModel(this._repository) : super(const AuthState(isLoading: true)) {
    initialize();
  }

  final AuthRepository _repository;

  Future<void> initialize() async {
    try {
      final token = await _repository.readToken();
      if (token == null) {
        state = const AuthState(isInitialized: true);
        return;
      }
      final user = await _repository.me(token);
      state = AuthState(user: user, token: token, isInitialized: true);
    } catch (_) {
      await _repository.logout();
      state = const AuthState(isInitialized: true);
    }
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final result = await _repository.login(email: email, password: password);
      state = AuthState(user: result.$2, token: result.$1, isInitialized: true);
      return true;
    } catch (error) {
      state = state.copyWith(
        isLoading: false,
        error: error.toString(),
        isInitialized: true,
      );
      return false;
    }
  }

  Future<bool> register({
    required String fullName,
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _repository.register(
        fullName: fullName,
        email: email,
        password: password,
      );
      state = state.copyWith(isLoading: false, isInitialized: true);
      return true;
    } catch (error) {
      state = state.copyWith(
        isLoading: false,
        error: error.toString(),
        isInitialized: true,
      );
      return false;
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    state = const AuthState(isInitialized: true);
  }
}

final authViewModelProvider = StateNotifierProvider<AuthViewModel, AuthState>((ref) {
  return AuthViewModel(ref.read(authRepositoryProvider));
});
