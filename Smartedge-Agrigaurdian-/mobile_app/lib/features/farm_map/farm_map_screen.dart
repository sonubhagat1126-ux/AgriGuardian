import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Farm Map Screen - Placeholder
/// TODO: Add flutter_map + VEDAS NDVI overlay + interactive farm plots
class FarmMapScreen extends StatelessWidget {
  const FarmMapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Farm Map")),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.map_rounded, size: 64, color: AppColors.textMuted),
            SizedBox(height: 16),
            Text(
              "Farm Map + Satellite View\n(Coming Soon)",
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}