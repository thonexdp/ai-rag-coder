import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/presentation/auth_view_model.dart';
import '../../chat/presentation/chat_screen.dart';
import '../../documents/presentation/documents_screen.dart';
import '../../schedule/presentation/schedule_screen.dart';
import '../../settings/presentation/settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authViewModelProvider);
    if (!authState.isAuthenticated) {
      Future.microtask(() => Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false));
      return const SizedBox.shrink();
    }

    final tabs = <Widget>[
      const ChatScreen(),
      if (authState.user?.isStudent ?? false) const ScheduleScreen(),
      if (authState.user?.isAdmin ?? false) const DocumentsScreen(),
      const SettingsScreen(),
    ];

    final items = <NavigationDestination>[
      const NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Chat'),
      if (authState.user?.isStudent ?? false)
        const NavigationDestination(icon: Icon(Icons.calendar_today), label: 'Schedule'),
      if (authState.user?.isAdmin ?? false)
        const NavigationDestination(icon: Icon(Icons.folder_outlined), label: 'Docs'),
      const NavigationDestination(icon: Icon(Icons.settings_outlined), label: 'Settings'),
    ];

    return Scaffold(
      body: tabs[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        destinations: items,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
      ),
    );
  }
}
