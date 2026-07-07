import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/chat_models.dart';
import '../../settings/presentation/settings_view_model.dart';
import '../../../core/services/voice_service.dart'; // AppLanguage + SpeakResult
import 'chat_view_model.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController(); // Fix #11 — auto-scroll
  String _lastSyncedVoiceDraft = '';

  @override
  void initState() {
    super.initState();
    // Fix #5 — rebuild send button when text changes
    _controller.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // Scrolls to the newest message at the bottom
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(chatViewModelProvider);
    final settingsState = ref.watch(settingsViewModelProvider);

    if (state.voiceDraft != _lastSyncedVoiceDraft) {
      _lastSyncedVoiceDraft = state.voiceDraft;
      _controller.value = TextEditingValue(
        text: state.voiceDraft,
        selection: TextSelection.collapsed(offset: state.voiceDraft.length),
      );
    }

    // Fix #1 — scroll to bottom whenever messages change
    if (state.messages.isNotEmpty) _scrollToBottom();

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chat'),
        actions: [
          // Fix #6 + #7 — styled dropdown using AppLanguage enum
          DropdownButtonHideUnderline(
            child: DropdownButton<AppLanguage>(
              value: state.language,
              icon: const Icon(Icons.language, size: 18),
              borderRadius: BorderRadius.circular(8),
              items: const [
                DropdownMenuItem(
                  value: AppLanguage.english,
                  child: Text('English'),
                ),
                DropdownMenuItem(
                  value: AppLanguage.tagalog,
                  child: Text('Filipino'),
                ),
                DropdownMenuItem(
                  value: AppLanguage.bisaya,
                  child: Text('Bisaya'),
                ),
              ],
              onChanged: (value) {
                if (value != null) {
                  ref.read(chatViewModelProvider.notifier).setLanguage(value);
                }
              },
            ),
          ),
          IconButton(
            onPressed: () =>
                ref.read(chatViewModelProvider.notifier).startNewChat(),
            icon: const Icon(Icons.edit_square),
            tooltip: 'New chat',
          ),
          IconButton(
            onPressed: () => _showHistory(context),
            icon: const Icon(Icons.history),
            tooltip: 'Chat history',
          ),
        ],
      ),
      body: Column(
        children: [
          // Fix #9 — dismissible error banner
          if (state.error != null)
            MaterialBanner(
              content: Text(state.error!),
              backgroundColor: Theme.of(context).colorScheme.errorContainer,
              leading: Icon(
                Icons.error_outline,
                color: Theme.of(context).colorScheme.error,
              ),
              actions: [
                TextButton(
                  onPressed: () =>
                      ref.read(chatViewModelProvider.notifier).clearError(),
                  child: const Text('Dismiss'),
                ),
              ],
            ),

          Expanded(
            child: ListView.builder(
              controller: _scrollController, // Fix #11
              padding: const EdgeInsets.all(16),
              // messages + optional typing indicator at end
              itemCount: state.messages.length + (state.isSending ? 1 : 0),
              itemBuilder: (context, index) {
                // Fix #2 — typing indicator as last item
                if (state.isSending && index == state.messages.length) {
                  return const Align(
                    alignment: Alignment.centerLeft,
                    child: _TypingIndicator(),
                  );
                }

                final item = state.messages[index];
                final isUser = item.role == 'user';

                return Align(
                  alignment: isUser
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: ConstrainedBox(
                    // Fix #10 — responsive max width instead of hardcoded 520
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.82,
                    ),
                    child: Card(
                      color: isUser
                          ? Theme.of(context).colorScheme.primaryContainer
                          : null,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item.content),

                            // Fix #3 + #4 — TTS button on AI replies only
                            if (!isUser)
                              _VoicePlayButton(
                                text: item.content,
                                language: state.language,
                              ),

                            if (settingsState.showChatSources &&
                                item.sources.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              ...item.sources.map(
                                (source) => _SourceCard(
                                  source,
                                  showSnippet:
                                      settingsState.showChatSourceSnippets,
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

          // Input bar
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
                      hintText: 'Ask about policies, schedules, announcements…',
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 12),

                // Mic button
                IconButton.filledTonal(
                  tooltip: state.isListening ? 'Stop listening' : 'Voice input',
                  onPressed: () async {
                    if (state.isListening) {
                      await ref
                          .read(chatViewModelProvider.notifier)
                          .stopVoiceInput();
                    } else {
                      await ref
                          .read(chatViewModelProvider.notifier)
                          .startVoiceInput((_) {});
                    }
                  },
                  icon: Icon(state.isListening ? Icons.mic_off : Icons.mic),
                ),
                const SizedBox(width: 8),

                // Fix #5 — disabled when empty or already sending
                FilledButton(
                  onPressed:
                      (state.isSending || _controller.text.trim().isEmpty)
                      ? null
                      : _sendMessage,
                  child: Text(state.isSending ? 'Sending…' : 'Send'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    _lastSyncedVoiceDraft = '';
    _controller.clear();
    ref.read(chatViewModelProvider.notifier).sendMessage(text);
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
                        Text(
                          'Chat history',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const Spacer(),
                        TextButton.icon(
                          onPressed: () async {
                            final confirmed = await _confirmClearAll(context);
                            if (!confirmed || !context.mounted) return;
                            await ref
                                .read(chatViewModelProvider.notifier)
                                .deleteAllHistory();
                            if (context.mounted) Navigator.pop(context);
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
                                await ref
                                    .read(chatViewModelProvider.notifier)
                                    .loadSession(session.id);
                              },
                              trailing: IconButton(
                                icon: const Icon(Icons.delete_outline),
                                tooltip: 'Delete chat',
                                onPressed: () async {
                                  final confirmed = await _confirmDeleteSession(
                                    context,
                                    session.title,
                                  );
                                  if (!confirmed) return;
                                  await ref
                                      .read(chatViewModelProvider.notifier)
                                      .deleteSession(session.id);
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
        content: const Text(
          'This will permanently remove all saved chat sessions on this account.',
        ),
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

// ── Typing indicator ──────────────────────────────────────────────────────────
// Fix #2 — animated dots shown while AI is generating a response
class _TypingIndicator extends StatefulWidget {
  const _TypingIndicator();

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _anim = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 900),
  )..repeat();

  @override
  void dispose() {
    _anim.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          child: AnimatedBuilder(
            animation: _anim,
            builder: (_, __) => Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                final opacity = ((_anim.value * 3 - i) % 1.0).clamp(0.2, 1.0);
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 3),
                  child: Opacity(
                    opacity: opacity,
                    child: Container(
                      width: 7,
                      height: 7,
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primary,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
      ),
    );
  }
}

// ── TTS play button on AI messages ────────────────────────────────────────────
// Fix #3 + #4 — calls VoiceService.speak(), handles Bisaya gracefully
class _VoicePlayButton extends ConsumerWidget {
  const _VoicePlayButton({required this.text, required this.language});

  final String text;
  final AppLanguage language;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final voiceService = ref.read(voiceServiceProvider);
    final canPlay = voiceService.canSpeak(language);

    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Tooltip(
        // Show reason when Bisaya voice is unavailable
        message: canPlay ? 'Read aloud' : 'Voice unavailable for Bisaya',
        child: IconButton(
          iconSize: 18,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
          icon: Icon(
            canPlay ? Icons.volume_up_outlined : Icons.volume_off_outlined,
            color: canPlay
                ? Theme.of(context).colorScheme.primary
                : Theme.of(context).colorScheme.outline,
          ),
          onPressed: canPlay
              ? () async {
                  final result = await voiceService.speak(
                    text,
                    language: language,
                  );
                  // SpeakResult.skippedNoVoice shouldn't reach here
                  // since we check canSpeak() above, but guard anyway
                  if (result == SpeakResult.skippedNoVoice && context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Voice not available for this language.'),
                      ),
                    );
                  }
                }
              : null,
        ),
      ),
    );
  }
}

// ── Source card (unchanged) ───────────────────────────────────────────────────
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
