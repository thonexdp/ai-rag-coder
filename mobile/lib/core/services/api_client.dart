import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../constants/app_constants.dart';

class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;
  static const _requestTimeout = Duration(seconds: 45);
  static const _uploadTimeout = Duration(seconds: 90);

  Uri _uri(String path) => Uri.parse('${AppConstants.apiBaseUrl}$path');

  Future<Map<String, dynamic>> getJson(String path, {String? token}) async {
    final response = await _send(
      _client.get(_uri(path), headers: _headers(token)),
      timeout: _requestTimeout,
    );
    return _decodeObject(response);
  }

  Future<List<dynamic>> getJsonList(String path, {String? token}) async {
    final response = await _send(
      _client.get(_uri(path), headers: _headers(token)),
      timeout: _requestTimeout,
    );
    return _decodeList(response);
  }

  Future<Map<String, dynamic>> postJson(
    String path, {
    required Map<String, dynamic> body,
    String? token,
  }) async {
    final response = await _send(
      _client.post(
        _uri(path),
        headers: _headers(token),
        body: jsonEncode(body),
      ),
      timeout: _requestTimeout,
    );
    return _decodeObject(response);
  }

  Future<void> delete(String path, {String? token}) async {
    final response = await _send(
      _client.delete(_uri(path), headers: _headers(token)),
      timeout: _requestTimeout,
    );
    if (response.statusCode >= 400) {
      throw ApiException(_extractError(response));
    }
  }

  Future<Map<String, dynamic>> postMultipart(
    String path, {
    required String fieldName,
    required List<int> bytes,
    required String filename,
    String? token,
    Map<String, String>? fields,
  }) async {
    final request = http.MultipartRequest('POST', _uri(path));
    request.headers.addAll(_headers(token, isJson: false));
    if (fields != null) {
      request.fields.addAll(fields);
    }
    request.files.add(
      http.MultipartFile.fromBytes(fieldName, bytes, filename: filename),
    );

    final streamed = await _sendStream(request.send(), timeout: _uploadTimeout);
    final response = await _send(
      http.Response.fromStream(streamed),
      timeout: _uploadTimeout,
    );
    return _decodeObject(response);
  }

  Future<http.Response> _send(
    Future<http.Response> request, {
    required Duration timeout,
  }) async {
    try {
      return await request.timeout(timeout);
    } on TimeoutException {
      throw ApiException('Request timed out. Please try again.');
    } on http.ClientException catch (error) {
      throw ApiException(error.message);
    }
  }

  Future<http.StreamedResponse> _sendStream(
    Future<http.StreamedResponse> request, {
    required Duration timeout,
  }) async {
    try {
      return await request.timeout(timeout);
    } on TimeoutException {
      throw ApiException('Upload timed out. Please try again.');
    } on http.ClientException catch (error) {
      throw ApiException(error.message);
    }
  }

  Map<String, String> _headers(String? token, {bool isJson = true}) {
    final headers = <String, String>{};
    if (isJson) {
      headers['Content-Type'] = 'application/json';
    }
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Map<String, dynamic> _decodeObject(http.Response response) {
    final body = response.body.isEmpty
        ? <String, dynamic>{}
        : jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw ApiException(body['detail']?.toString() ?? 'Request failed');
    }
    return body;
  }

  List<dynamic> _decodeList(http.Response response) {
    if (response.statusCode >= 400) {
      throw ApiException(_extractError(response));
    }
    return response.body.isEmpty ? <dynamic>[] : jsonDecode(response.body) as List<dynamic>;
  }

  String _extractError(http.Response response) {
    if (response.body.isEmpty) {
      return 'Request failed';
    }
    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) {
      return decoded['detail']?.toString() ?? 'Request failed';
    }
    return 'Request failed';
  }
}

class ApiException implements Exception {
  ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}
