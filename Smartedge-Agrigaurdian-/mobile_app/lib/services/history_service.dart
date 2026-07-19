import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// HistoryService — Local storage for disease scans and analytics
class HistoryService {
  static const String _storageKey = "agri_scan_history_v1";

  /// Saves a new disease scan to local history
  static Future<void> addScanRecord({
    required String diseaseName,
    required double confidence,
    required Map<String, dynamic> actionPlan,
    Map<String, dynamic>? sensorData,
    String? imagePath,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> rawList = prefs.getStringList(_storageKey) ?? [];

    final record = {
      "id": DateTime.now().millisecondsSinceEpoch.toString(),
      "disease_name": diseaseName,
      "confidence": confidence,
      "timestamp": DateTime.now().toIso8601String(),
      "action_plan": actionPlan,
      "sensor_data": sensorData ?? {},
      "image_path": imagePath ?? "",
    };

    rawList.insert(0, jsonEncode(record)); // Newest first

    // Keep up to 50 historical records
    if (rawList.length > 50) {
      rawList.removeLast();
    }

    await prefs.setStringList(_storageKey, rawList);
  }

  /// Retrieves list of past disease scan records
  static Future<List<Map<String, dynamic>>> getScanHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> rawList = prefs.getStringList(_storageKey) ?? [];

    return rawList
        .map((str) => jsonDecode(str) as Map<String, dynamic>)
        .toList();
  }

  /// Clears scan history
  static Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_storageKey);
  }
}
