class ScheduleItem {
  const ScheduleItem({
    required this.courseCode,
    required this.courseTitle,
    required this.weekday,
    required this.startTime,
    required this.endTime,
    required this.room,
  });

  final String courseCode;
  final String courseTitle;
  final String weekday;
  final String startTime;
  final String endTime;
  final String? room;

  factory ScheduleItem.fromJson(Map<String, dynamic> json) {
    return ScheduleItem(
      courseCode: json['course_code'] as String? ?? '',
      courseTitle: json['course_title'] as String? ?? '',
      weekday: json['weekday'] as String? ?? '',
      startTime: json['start_time'] as String? ?? '',
      endTime: json['end_time'] as String? ?? '',
      room: json['room'] as String?,
    );
  }
}
