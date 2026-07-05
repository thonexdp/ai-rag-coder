import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/presentation/auth_view_model.dart';
import '../data/schedule_repository.dart';
import '../domain/schedule_item.dart';

final scheduleRepositoryProvider = Provider<ScheduleRepository>((ref) {
  return ScheduleRepository(ref.read(apiClientProvider));
});

class ScheduleState {
  const ScheduleState({
    this.items = const [],
    this.isLoading = false,
    this.error,
  });

  final List<ScheduleItem> items;
  final bool isLoading;
  final String? error;

  ScheduleState copyWith({
    List<ScheduleItem>? items,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return ScheduleState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : error ?? this.error,
    );
  }
}

class ScheduleViewModel extends StateNotifier<ScheduleState> {
  ScheduleViewModel(this._ref, this._repository) : super(const ScheduleState()) {
    load();
  }

  final Ref _ref;
  final ScheduleRepository _repository;

  Future<void> load() async {
    final token = _ref.read(authViewModelProvider).token;
    if (token == null) {
      return;
    }
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final items = await _repository.getMySchedule(token);
      state = state.copyWith(items: items, isLoading: false);
    } catch (error) {
      state = state.copyWith(isLoading: false, error: error.toString());
    }
  }
}

final scheduleViewModelProvider = StateNotifierProvider<ScheduleViewModel, ScheduleState>((ref) {
  return ScheduleViewModel(ref, ref.read(scheduleRepositoryProvider));
});
