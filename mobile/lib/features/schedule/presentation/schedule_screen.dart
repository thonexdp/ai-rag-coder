import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'schedule_view_model.dart';

class ScheduleScreen extends ConsumerWidget {
  const ScheduleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(scheduleViewModelProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tomorrow\'s Schedule'),
        actions: [
          IconButton(
            onPressed: () => ref.read(scheduleViewModelProvider.notifier).load(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: state.isLoading && state.items.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (state.error != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(state.error!, style: const TextStyle(color: Colors.red)),
                  ),
                if (state.items.isEmpty)
                  const Card(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Text('No classes found for tomorrow.'),
                    ),
                  ),
                ...state.items.map(
                  (item) => Card(
                    child: ListTile(
                      title: Text('${item.courseCode} · ${item.courseTitle}'),
                      subtitle: Text(
                        '${item.weekday} · ${item.startTime} - ${item.endTime}'
                        '${item.room == null ? '' : '\nRoom ${item.room}'}',
                      ),
                      isThreeLine: item.room != null,
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}
