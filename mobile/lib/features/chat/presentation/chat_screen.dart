import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/chat_models.dart';
import '../../settings/presentation/settings_view_model.dart';
import 'chat_view_model.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(chatViewModelProvider);
    final settingsState = ref.watch(settingsViewModelProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chat'),
        actions: [
          DropdownButton<String>(
            value: state.language,
            items: const [
              DropdownMenuItem(value: 'en', child: Text('English')),
              DropdownMenuItem(value: 'fil', child: Text('Filipino')),
              DropdownMenuItem(value: 'ceb', child: Text('Bisaya')),
            ],
            onChanged: (value) {
              if (value != null) {
                ref.read(chatViewModelProvider.notifier).setLanguage(value);
              }
            },
          ),
          IconButton(
            onPressed: () => ref.read(chatViewModelProvider.notifier).startNewChat(),
            icon: const Icon(Icons.edit_square),
            tooltip: 'New chat',
          ),
          IconButton(
            onPressed: () => _showHistory(context),
            icon: const Icon(Icons.history),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: state.messages.length,
              itemBuilder: (context, index) {
                final item = state.messages[index];
                final isUser = item.role == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 520),
                    child: Card(
                      color: isUser ? Theme.of(context).colorScheme.primaryContainer : null,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item.content),
                            if (settingsState.showChatSources && item.sources.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              ...item.sources.map(
                                (source) => _SourceCard(
                                  source,
                                  showSnippet: settingsState.showChatSourceSnippets,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(state.error!, style: const TextStyle(color: Colors.red)),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    minLines: 1,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      hintText: 'Ask about policies, schedules, announcements, or uploaded documents...',
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                IconButton.filledTonal(
                  onPressed: () async {
                    if (state.isListening) {
                      await ref.read(chatViewModelProvider.notifier).stopVoiceInput();
                    } else {
                      await ref.read(chatViewModelProvider.notifier).startVoiceInput((text) {
                        _controller.text = text;
                      });
                    }
                  },
                  icon: Icon(state.isListening ? Icons.mic_off : Icons.mic),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: state.isSending
                      ? null
                      : () async {
                          final text = _controller.text;
                          _controller.clear();
                          await ref.read(chatViewModelProvider.notifier).sendMessage(text);
                        },
                  child: Text(state.isSending ? 'Sending...' : 'Send'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showHistory(BuildContext context) {
    return showModalBottomSheet<void>(
      context: context,
      builder: (context) {
        return Consumer(
          builder: (context, ref, _) {
            final state = ref.watch(chatViewModelProvider);
            if (state.sessions.isEmpty) {
              return const Padding(
                padding: EdgeInsets.all(24),
                child: Text('No chat history yet.'),
              );
            }

            return SafeArea(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 8, 8),
                    child: Row(
                      children: [
                        Text('Chat history', style: Theme.of(context).textTheme.titleMedium),
                        const Spacer(),
                        TextButton.icon(
                          onPressed: () async {
                            final confirmed = await _confirmClearAll(context);
                            if (!confirmed || !context.mounted) {
                              return;
                            }
                            await ref.read(chatViewModelProvider.notifier).deleteAllHistory();
                            if (context.mounted) {
                              Navigator.pop(context);
                            }
                          },
                          icon: const Icon(Icons.delete_sweep_outlined),
                          label: const Text('Clear all'),
                        ),
                      ],
                    ),
                  ),
                  Flexible(
                    child: ListView(
                      shrinkWrap: true,
                      children: state.sessions
                          .map(
                            (session) => ListTile(
                              title: Text(session.title),
                              onTap: () async {
                                Navigator.pop(context);
                                await ref.read(chatViewModelProvider.notifier).loadSession(session.id);
                              },
                              trailing: IconButton(
                                icon: const Icon(Icons.delete_outline),
                                tooltip: 'Delete chat',
                                onPressed: () async {
                                  final confirmed = await _confirmDeleteSession(context, session.title);
                                  if (!confirmed) {
                                    return;
                                  }
                                  await ref.read(chatViewModelProvider.notifier).deleteSession(session.id);
                                },
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Future<bool> _confirmDeleteSession(BuildContext context, String title) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete chat?'),
        content: Text('Remove "$title" from your chat history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  Future<bool> _confirmClearAll(BuildContext context) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear all history?'),
        content: const Text('This will permanently remove all saved chat sessions on this account.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Clear all'),
          ),
        ],
      ),
    );
    return result ?? false;
  }
}

class _SourceCard extends StatelessWidget {
  const _SourceCard(this.source, {required this.showSnippet});

  final ChatSource source;
  final bool showSnippet;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(source.title, style: Theme.of(context).textTheme.titleSmall),
          if (source.page != null) Text('Page ${source.page}'),
          if (showSnippet && source.snippet.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(source.snippet),
          ],
        ],
      ),
    );
  }
}
