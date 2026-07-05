import 'package:flutter/foundation.dart';

class AppConstants {
  static const appName = 'AI School Assistant';
  static const _configuredApiBaseUrl = String.fromEnvironment('API_BASE_URL');

  static String get apiBaseUrl {
    if (_configuredApiBaseUrl.isNotEmpty) {
      return _configuredApiBaseUrl;
    }
    if (kIsWeb) {
      return 'http://localhost:9000/api/v1';
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:9000/api/v1';
      default:
        return 'http://localhost:9000/api/v1';
    }
  }
}
