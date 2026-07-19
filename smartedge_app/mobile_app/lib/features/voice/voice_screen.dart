import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Voice Assistant Screen - Placeholder
/// TODO: Add speech_to_text + flutter_tts + backend (kb_matcher/Ollama) integration
class VoiceScreen extends StatelessWidget {
  const VoiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("AI Crop Doctor")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.primaryGreen,
              ),
              child: const Icon(Icons.mic_rounded, size: 48, color: Colors.white),
            ),
            const SizedBox(height: 20),
            const Text(
              "Bolo, kya poochna hai?\n(Coming Soon)",
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}