import '../../../core/services/api_client.dart';
import '../../../core/services/secure_storage_service.dart';
import '../domain/auth_user.dart';

class AuthRepository {
  AuthRepository(this._apiClient, this._storage);

  final ApiClient _apiClient;
  final SecureStorageService _storage;

  Future<(String, AuthUser)> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.postJson(
      '/auth/login',
      body: {
        'email': email,
        'password': password,
      },
    );
    final token = response['access_token'] as String;
    await _storage.saveToken(token);
    return (token, AuthUser.fromJson(response['user'] as Map<String, dynamic>));
  }

  Future<AuthUser> register({
    required String fullName,
    required String email,
    required String password,
    String role = 'student',
  }) async {
    final response = await _apiClient.postJson(
      '/auth/register',
      body: {
        'full_name': fullName,
        'email': email,
        'password': password,
        'role': role,
      },
    );
    return AuthUser.fromJson(response);
  }

  Future<String?> readToken() => _storage.readToken();

  Future<AuthUser> me(String token) async {
    final response = await _apiClient.getJson('/auth/me', token: token);
    return AuthUser.fromJson(response);
  }

  Future<void> logout() => _storage.clearToken();
}
