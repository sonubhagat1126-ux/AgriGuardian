import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// TTSService — Hindi Text-To-Speech Service
/// Speaks crop advisories and chatbot answers out loud in clear Hindi.
class TTSService {
  static final FlutterTts _flutterTts = FlutterTts();
  static bool _isInitialized = false;
  static bool isSpeaking = false;

  static Future<void> init() async {
    if (_isInitialized) return;

    try {
      if (!kIsWeb && (Platform.isAndroid || Platform.isIOS)) {
        await _flutterTts.setLanguage("hi-IN");
        await _flutterTts.setSpeechRate(0.45); // Comfortable reading speed
        await _flutterTts.setVolume(1.0);
        await _flutterTts.setPitch(1.0);
      }

      _flutterTts.setStartHandler(() {
        isSpeaking = true;
      });

      _flutterTts.setCompletionHandler(() {
        isSpeaking = false;
      });

      _flutterTts.setErrorHandler((msg) {
        isSpeaking = false;
      });

      _isInitialized = true;
    } catch (e) {
      debugPrint("TTS Initialization Warning: $e");
    }
  }

  /// Speaks Hindi text aloud
  static Future<void> speak(String text) async {
    await init();
    if (text.isEmpty) return;

    // Remove markdown symbols before reading out loud
    final cleanText = text
        .replaceAll("*", "")
        .replaceAll("#", "")
        .replaceAll("-", "")
        .replaceAll("•", "")
        .replaceAll("_", "");

    try {
      await _flutterTts.stop();
      await _flutterTts.speak(cleanText);
      isSpeaking = true;
    } catch (e) {
      debugPrint("TTS Speak Error: $e");
    }
  }

  /// Stops current speech
  static Future<void> stop() async {
    try {
      await _flutterTts.stop();
      isSpeaking = false;
    } catch (e) {
      debugPrint("TTS Stop Error: $e");
    }
  }
}
