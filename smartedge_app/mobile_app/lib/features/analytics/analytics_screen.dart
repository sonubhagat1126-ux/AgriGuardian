import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Analytics Screen - Placeholder
/// TODO: Add fl_chart graphs - health score trend, moisture trend, NDVI trend
class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Analytics")),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.bar_chart_rounded, size: 64, color: AppColors.textMuted),
            SizedBox(height: 16),
            Text(
              "Health & Moisture Trends\n(Coming Soon)",
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}