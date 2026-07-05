import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/core/services/api_client.dart';
import 'package:mobile/core/services/secure_storage_service.dart';
import 'package:mobile/features/auth/data/auth_repository.dart';
import 'package:mobile/features/auth/presentation/auth_view_model.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('renders login experience', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authViewModelProvider.overrideWith((ref) => _FakeAuthViewModel()),
        ],
        child: const SchoolAssistantApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('AI School Assistant'), findsOneWidget);
    expect(find.text('Login'), findsOneWidget);
  });
}

class _FakeAuthViewModel extends AuthViewModel {
  _FakeAuthViewModel() : super(_FakeAuthRepository());

  @override
  Future<void> initialize() async {
    state = const AuthState(isInitialized: true);
  }
}

class _FakeAuthRepository extends AuthRepository {
  _FakeAuthRepository() : super(ApiClient(), SecureStorageService());

  @override
  Future<String?> readToken() async => null;
}
