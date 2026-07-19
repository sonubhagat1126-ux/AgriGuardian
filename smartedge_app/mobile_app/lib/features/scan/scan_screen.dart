import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Scan Screen - Placeholder
/// TODO: Add camera preview + leaf disease detection (LiteRT/TFLite model)
class ScanScreen extends StatelessWidget {
  const ScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Scan Leaf")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.camera_alt_rounded, size: 64, color: AppColors.textMuted),
            const SizedBox(height: 16),
            const Text(
              "Leaf Disease Detection\n(Coming Soon)",
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.camera_alt),
              label: const Text("Open Camera"),
            ),
          ],
        ),
      ),
    );
  }
}