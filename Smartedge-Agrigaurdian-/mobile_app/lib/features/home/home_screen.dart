import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Home Dashboard Screen
/// Shows: Crop Health Score, Sensor Data, Weather Summary, Quick Alerts
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // TODO: Replace with real data from backend (Arduino sensors + weather_advisor.py)
    const double healthScore = 82;
    const String moisture = "45%";
    const String temperature = "29°C";
    const String humidity = "60%";

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            const Text(
              "Namaste, Devansh 🌾",
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              "Aapke khet ka aaj ka haal",
              style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
            ),
            const SizedBox(height: 20),

            // Crop Health Score Card
            _buildHealthScoreCard(healthScore),
            const SizedBox(height: 16),

            // Sensor Data Row
            Row(
              children: [
                Expanded(
                  child: _buildSensorCard(
                    icon: Icons.water_drop_rounded,
                    label: "Moisture",
                    value: moisture,
                    color: AppColors.lightGreen,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSensorCard(
                    icon: Icons.thermostat_rounded,
                    label: "Temperature",
                    value: temperature,
                    color: AppColors.warning,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSensorCard(
                    icon: Icons.air_rounded,
                    label: "Humidity",
                    value: humidity,
                    color: AppColors.accentGreen,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Weather + Irrigation Card
            _buildWeatherCard(),
            const SizedBox(height: 20),

            // Quick Alerts
            const Text(
              "Quick Alerts",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 10),
            _buildAlertTile(
              icon: Icons.water_drop_outlined,
              text: "Aaj shaam irrigation ki zarurat hai",
              severity: "medium",
            ),
            const SizedBox(height: 8),
            _buildAlertTile(
              icon: Icons.check_circle_outline,
              text: "Koi disease detect nahi hua is hafte",
              severity: "low",
            ),

            const SizedBox(height: 24),

            // Quick Action Buttons
            Row(
              children: [
                Expanded(
                  child: _buildQuickActionButton(
                    icon: Icons.camera_alt_rounded,
                    label: "Scan Leaf",
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildQuickActionButton(
                    icon: Icons.mic_rounded,
                    label: "Ask AI",
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthScoreCard(double score) {
    final Color scoreColor = AppTheme.getHealthColor(score);
    final String statusText =
        score >= 70 ? "Healthy" : (score >= 40 ? "Needs Attention" : "Critical");

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: scoreColor.withValues(alpha: 0.3), width: 1.5),
      ),
      child: Row(
        children: [
          // Score circle
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: scoreColor.withValues(alpha: 0.15),
              border: Border.all(color: scoreColor, width: 3),
            ),
            child: Center(
              child: Text(
                score.toInt().toString(),
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: scoreColor,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Crop Health Score",
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
                ),
                const SizedBox(height: 4),
                Text(
                  statusText,
                  style: TextStyle(
                    color: scoreColor,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  "Based on soil, weather & leaf data",
                  style: TextStyle(color: AppColors.textMuted, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSensorCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 26),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(color: AppColors.textMuted, fontSize: 11),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.primaryGreen.withValues(alpha: 0.3), AppColors.cardBackground],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          const Icon(Icons.cloud_rounded, color: AppColors.accentGreen, size: 36),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Aaj Baarish Ka Chance Kam Hai",
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  "Irrigation Suggestion: Shaam 12 min paani do",
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertTile({
    required IconData icon,
    required String text,
    required String severity,
  }) {
    Color color = severity == "high"
        ? AppColors.danger
        : severity == "medium"
            ? AppColors.warning
            : AppColors.healthy;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(14),
        border: Border(left: BorderSide(color: color, width: 4)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(color: AppColors.textPrimary, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton({required IconData icon, required String label}) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 18),
      decoration: BoxDecoration(
        color: AppColors.primaryGreen,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white, size: 26),
          const SizedBox(height: 6),
          Text(
            label,
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}