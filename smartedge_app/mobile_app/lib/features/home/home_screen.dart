import 'dart:async';
import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

/// Home Dashboard Screen
/// Shows: Crop Health Score, Sensor Data, Weather Summary, Quick Alerts
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  Timer? _timer;

  // Dynamic State variables
  double _healthScore = 82.0;
  String _moisture = "45%";
  String _temperature = "29°C";
  String _humidity = "60%";
  String _serverIpDisplay = "10.0.2.2:8000";

  @override
  void initState() {
    super.initState();
    _loadServerIp();
    _fetchData();
    // Poll data every 2 seconds
    _timer = Timer.periodic(const Duration(seconds: 2), (timer) {
      _fetchData();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _loadServerIp() async {
    final url = await _apiService.getServerUrl();
    setState(() {
      _serverIpDisplay = url.replaceAll("http://", "");
    });
  }

  Future<void> _fetchData() async {
    final data = await _apiService.fetchSensorData();
    if (data != null && mounted) {
      setState(() {
        final double ndvi = (data["vegetation_ndvi"] ?? 0.65).toDouble();
        final double soilMoisture = (data["soil_moisture"] ?? 45).toDouble();
        final double temp = (data["temperature"] ?? 29.0).toDouble();
        final double hum = (data["humidity"] ?? 60.0).toDouble();

        // Calculate dynamic health score based on NDVI and moisture
        _healthScore = (ndvi * 70.0) + (soilMoisture * 0.3);
        _healthScore = _healthScore.clamp(0.0, 100.0);

        _moisture = "${soilMoisture.toInt()}%";
        _temperature = "${temp.toStringAsFixed(1)}°C";
        _humidity = "${hum.toStringAsFixed(1)}%";
      });
    }
  }

  void _showSettingsDialog() {
    final controller = TextEditingController(text: _serverIpDisplay);
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: AppColors.cardBackground,
          title: const Text(
            "Configure Server IP",
            style: TextStyle(color: AppColors.textPrimary),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                "Enter your laptop's local network IP to sync live hardware sensors.",
                style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: controller,
                style: const TextStyle(color: AppColors.textPrimary),
                decoration: const InputDecoration(
                  labelText: "Server Address",
                  labelStyle: TextStyle(color: AppColors.textMuted),
                  hintText: "192.168.1.100:8000",
                  hintStyle: TextStyle(color: AppColors.textMuted),
                  enabledBorder: UnderlineInputBorder(
                    borderSide: BorderSide(color: AppColors.textMuted),
                  ),
                  focusedBorder: UnderlineInputBorder(
                    borderSide: BorderSide(color: AppColors.primaryGreen),
                  ),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel", style: TextStyle(color: AppColors.textSecondary)),
            ),
            TextButton(
              onPressed: () async {
                await _apiService.setServerIp(controller.text);
                await _loadServerIp();
                _fetchData();
                if (context.mounted) Navigator.pop(context);
              },
              child: const Text("Save", style: TextStyle(color: AppColors.primaryGreen, fontWeight: FontWeight.bold)),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with Settings Button
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Namaste, Devansh 🌾",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      "Aapke khet ka aaj ka haal",
                      style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.settings_rounded, color: AppColors.primaryGreen, size: 28),
                  onPressed: _showSettingsDialog,
                  tooltip: "Sync Server IP",
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Crop Health Score Card
            _buildHealthScoreCard(_healthScore),
            const SizedBox(height: 16),

            // Sensor Data Row
            Row(
              children: [
                Expanded(
                  child: _buildSensorCard(
                    icon: Icons.water_drop_rounded,
                    label: "Moisture",
                    value: _moisture,
                    color: AppColors.lightGreen,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSensorCard(
                    icon: Icons.thermostat_rounded,
                    label: "Temperature",
                    value: _temperature,
                    color: AppColors.warning,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildSensorCard(
                    icon: Icons.air_rounded,
                    label: "Humidity",
                    value: _humidity,
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
        border: Border.all(color: scoreColor.withOpacity(0.3), width: 1.5),
      ),
      child: Row(
        children: [
          // Score circle
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: scoreColor.withOpacity(0.15),
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
          colors: [AppColors.primaryGreen.withOpacity(0.3), AppColors.cardBackground],
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