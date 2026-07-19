import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String _defaultHost = kIsWeb ? "localhost:8000" : "10.0.2.2:8000"; // Default host depending on platform
  static const String _ipKey = "backend_server_ip";

  /// Gets the currently configured backend server URL (e.g. "http://192.168.1.100:8000")
  Future<String> getServerUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final ip = prefs.getString(_ipKey) ?? _defaultHost;
    return "http://$ip";
  }

  /// Sets/updates the backend server IP address
  Future<void> setServerIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_ipKey, ip.trim());
  }

  /// Fetches the latest live sensor and satellite data from the FastAPI backend
  Future<Map<String, dynamic>?> fetchSensorData() async {
    try {
      final baseUrl = await getServerUrl();
      final response = await http.get(
        Uri.parse("$baseUrl/api/data"),
        headers: {"Content-Type": "application/json"},
      ).timeout(const Duration(seconds: 3));

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }
    } catch (e) {
      print("Error fetching sensor data: $e");
    }
    return null;
  }

  /// Sends control commands to toggle pump status, auto-mode, or thresholds
  Future<bool> sendControlCommand(String action, dynamic value) async {
    try {
      final baseUrl = await getServerUrl();
      final response = await http.post(
        Uri.parse("$baseUrl/api/control"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({"action": action, "value": value}),
      ).timeout(const Duration(seconds: 3));

      if (response.statusCode == 200) {
        final resData = json.decode(response.body);
        return resData["status"] == "success";
      }
    } catch (e) {
      print("Error sending control command: $e");
    }
    return false;
  }
}
