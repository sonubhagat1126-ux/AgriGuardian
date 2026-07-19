import 'package:flutter/material.dart';
import '../../services/history_service.dart';

const Color kEmerald = Color(0xFF10B981);

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  List<Map<String, dynamic>> _history = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    final data = await HistoryService.getScanHistory();
    setState(() {
      _history = data;
      _isLoading = false;
    });
  }

  Future<void> _clearHistory() async {
    await HistoryService.clearHistory();
    await _loadHistory();
  }

  @override
  Widget build(BuildContext context) {
    final totalScans = _history.length;
    final healthyScans = _history.where((item) => (item["disease_name"] ?? "").toString().toLowerCase().contains("healthy")).length;
    final diseaseScans = totalScans - healthyScans;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Crop Health Analytics", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        actions: [
          if (_history.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
              onPressed: _clearHistory,
              tooltip: "Clear History",
            ),
        ],
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: kEmerald))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Overview Cards
                  Row(
                    children: [
                      _buildStatCard("Total Scans", "$totalScans", Icons.center_focus_strong, Colors.blueAccent),
                      const SizedBox(width: 12),
                      _buildStatCard("Diseased", "$diseaseScans", Icons.warning_amber_rounded, Colors.orangeAccent),
                      const SizedBox(width: 12),
                      _buildStatCard("Healthy", "$healthyScans", Icons.check_circle_outline, kEmerald),
                    ],
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    "Scan History & Timeline",
                    style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),

                  if (_history.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Center(
                        child: Text(
                          "No scans recorded yet.\nScan crop leaves using the Scan tab to build your history.",
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.white60, fontSize: 14),
                        ),
                      ),
                    )
                  else
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _history.length,
                      itemBuilder: (context, index) {
                        final item = _history[index];
                        final name = item["disease_name"] ?? "Unknown";
                        final conf = ((item["confidence"] ?? 0.0) * 100).toStringAsFixed(1);
                        final dateStr = item["timestamp"] ?? "";
                        final isHealthy = name.toString().toLowerCase().contains("healthy");

                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E293B),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(
                              color: isHealthy ? kEmerald.withValues(alpha: 0.3) : Colors.orangeAccent.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Row(
                            children: [
                              CircleAvatar(
                                backgroundColor: (isHealthy ? kEmerald : Colors.orangeAccent).withValues(alpha: 0.2),
                                child: Icon(
                                  isHealthy ? Icons.eco_rounded : Icons.bug_report_rounded,
                                  color: isHealthy ? kEmerald : Colors.orangeAccent,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      name,
                                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      "Confidence: $conf% • $dateStr",
                                      style: const TextStyle(color: Colors.white54, fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                ],
              ),
            ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(color: Colors.white60, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}