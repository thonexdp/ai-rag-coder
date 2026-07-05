import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/constants/app_constants.dart';
import 'core/routes/app_router.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/auth_view_model.dart';
import 'features/auth/presentation/login_screen.dart';
import 'features/home/presentation/home_screen.dart';

void main() {
  runApp(const ProviderScope(child: SchoolAssistantApp()));
}

class SchoolAssistantApp extends ConsumerWidget {
  const SchoolAssistantApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authViewModelProvider);

    return MaterialApp(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme(),
      routes: AppRouter.routes,
      home: _buildHome(authState),
    );
  }

  Widget _buildHome(AuthState authState) {
    if (!authState.isInitialized) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    return authState.isAuthenticated ? const HomeScreen() : const LoginScreen();
  }
}
