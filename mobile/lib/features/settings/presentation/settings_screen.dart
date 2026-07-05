import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/presentation/auth_view_model.dart';
import 'settings_view_model.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authViewModelProvider);
    final settingsState = ref.watch(settingsViewModelProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              title: Text(authState.user?.fullName ?? 'Guest'),
              subtitle: Text(authState.user?.email ?? ''),
              trailing: Text(authState.user?.role ?? ''),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Show source docs'),
                  subtitle: const Text('Display document source cards in chat replies.'),
                  value: settingsState.showChatSources,
                  onChanged: settingsState.isLoading
                      ? null
                      : (value) async {
                          await ref.read(settingsViewModelProvider.notifier).setShowChatSources(value);
                        },
                ),
                SwitchListTile(
                  title: const Text('Show source summary'),
                  subtitle: const Text('Display the source snippet text inside source cards.'),
                  value: settingsState.showChatSourceSnippets,
                  onChanged: settingsState.isLoading || !settingsState.showChatSources
                      ? null
                      : (value) async {
                          await ref.read(settingsViewModelProvider.notifier).setShowChatSourceSnippets(value);
                        },
                ),
                SwitchListTile(
                  title: const Text('Text to speech'),
                  subtitle: const Text('Speak assistant replies aloud without affecting microphone input.'),
                  value: settingsState.enableTextToSpeech,
                  onChanged: settingsState.isLoading
                      ? null
                      : (value) async {
                          await ref.read(settingsViewModelProvider.notifier).setEnableTextToSpeech(value);
                        },
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          FilledButton.tonal(
            onPressed: () async {
              await ref.read(authViewModelProvider.notifier).logout();
              if (context.mounted) {
                Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
              }
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}
