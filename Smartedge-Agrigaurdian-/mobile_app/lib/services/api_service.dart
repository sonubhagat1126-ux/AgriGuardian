import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

/// API Service - Central communication handler connecting the Flutter mobile app
/// to the Arduino UNO Q Python Central REST Server (port 5001).
class ApiService {
  // Replace with your Arduino UNO Q board / PC server IP address
  static const String baseUrl = "http://10.92.212.144:5001";
  static const Duration _timeout = Duration(seconds: 25);

  /// 1. YOLO Leaf Disease Detection
  /// Sends image multipart upload to POST /leaf/detect
  static Future<Map<String, dynamic>> detectLeafDisease(File imageFile) async {
    try {
      final uri = Uri.parse("$baseUrl/leaf/detect");
      final request = http.MultipartRequest("POST", uri);

      request.files.add(
        await http.MultipartFile.fromPath("image", imageFile.path),
      );

      final streamedResponse = await request.send().timeout(_timeout);
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          "status": "error",
          "message": "Server error: ${response.statusCode}",
        };
      }
    } catch (e) {
      return {
        "status": "error",
        "message": "Could not connect to Arduino UNO Q server: $e",
      };
    }
  }

  /// 2. AI Crop Doctor Advisory (Hindi Text + Action Plan)
  /// Sends JSON to POST /ai/crop-doctor
  static Future<Map<String, dynamic>> getCropDoctorAdvisory({
    required String disease,
    double confidence = 0.95,
    String? question,
  }) async {
    try {
      final uri = Uri.parse("$baseUrl/ai/crop-doctor");
      final response = await http
          .post(
            uri,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "disease": disease,
              "confidence": confidence,
              if (question != null && question.isNotEmpty) "question": question,
            }),
          )
          .timeout(_timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          "status": "error",
          "message": "Failed to get advisory: ${response.statusCode}",
        };
      }
    } catch (e) {
      return {
        "status": "error",
        "message": "Network error while fetching advisory: $e",
      };
    }
  }

  /// 3. Interactive AI Chatbot Q&A
  /// Sends JSON to POST /ai/chat
  static Future<Map<String, dynamic>> sendChatMessage({
    required String question,
    String? disease,
  }) async {
    try {
      final uri = Uri.parse("$baseUrl/ai/chat");
      final response = await http
          .post(
            uri,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "question": question,
              if (disease != null) "disease": disease,
            }),
          )
          .timeout(_timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return {
          "status": "error",
          "reply_hindi": "माफ़ कीजिये, सर्वर से जुड़ने में समस्या आई।",
        };
      }
    } catch (e) {
      return {
        "status": "error",
        "reply_hindi": "नेटवर्क समस्या: सर्वर तक पहुँच नहीं बन सकी।",
      };
    }
  }

  /// 4. Real-time Weather Indicators
  /// Calls GET /ai/weather
  static Future<Map<String, dynamic>?> getWeather() async {
    try {
      final uri = Uri.parse("$baseUrl/ai/weather");
      final response = await http.get(uri).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return data["weather"] as Map<String, dynamic>?;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// 5. Sensor Snapshot
  /// Calls GET /sensor
  static Future<Map<String, dynamic>?> getSensorData() async {
    try {
      final uri = Uri.parse("$baseUrl/sensor");
      final response = await http.get(uri).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return data["readings"] as Map<String, dynamic>?;
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}