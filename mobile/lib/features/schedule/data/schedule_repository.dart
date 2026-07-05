import '../../../core/services/api_client.dart';
import '../domain/schedule_item.dart';

class ScheduleRepository {
  ScheduleRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<List<ScheduleItem>> getMySchedule(String token) async {
    final response = await _apiClient.getJsonList('/students/me/schedule', token: token);
    return response
        .map((item) => ScheduleItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
