import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../services/api_service.dart';
import '../../services/tts_service.dart';
import '../../services/history_service.dart';

const Color kEmerald = Color(0xFF10B981);

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;
  bool _isLoading = false;

  Map<String, dynamic>? _scanResult;
  Map<String, dynamic>? _actionPlan;
  String? _advisoryHindi;
  bool _isSpeaking = false;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? file = await _picker.pickImage(
        source: source,
        imageQuality: 90,
      );
      if (file == null) return;

      setState(() {
        _selectedImage = File(file.path);
        _scanResult = null;
        _actionPlan = null;
        _advisoryHindi = null;
      });

      await _runDiseaseDetection(_selectedImage!);
    } catch (e) {
      _showSnackBar("Image pick error: $e");
    }
  }

  Future<void> _runDiseaseDetection(File imageFile) async {
    setState(() => _isLoading = true);

    final detectRes = await ApiService.detectLeafDisease(imageFile);
    setState(() => _isLoading = false);

    if (detectRes["status"] == "error") {
      _showSnackBar(detectRes["message"] ?? "Detection failed");
      return;
    }

    final double confidence = (detectRes["confidence"] as num? ?? 0.0).toDouble();
    final String label = detectRes["label"] as String? ?? "Unknown";

    // 70% Gate Filter Check
    if (confidence < 0.70) {
      _showLowConfidenceDialog(confidence);
      return;
    }

    // Fetch AI Crop Doctor Advisory (Hindi + Action Plan)
    setState(() => _isLoading = true);
    final doctorRes = await ApiService.getCropDoctorAdvisory(
      disease: label,
      confidence: confidence,
    );
    setState(() => _isLoading = false);

    setState(() {
      _scanResult = detectRes;
      _actionPlan = doctorRes["action_plan"] as Map<String, dynamic>?;
      _advisoryHindi = doctorRes["advisory_hindi"] as String?;
    });

    // Save to local history
    if (_actionPlan != null) {
      await HistoryService.addScanRecord(
        diseaseName: detectRes["disease_name"] ?? label,
        confidence: confidence,
        actionPlan: _actionPlan!,
        sensorData: doctorRes["sensor_data"] as Map<String, dynamic>?,
        imagePath: imageFile.path,
      );
    }
  }

  void _showLowConfidenceDialog(double confidence) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Colors.orangeAccent),
            SizedBox(width: 8),
            Text("Low Confidence", style: TextStyle(color: Colors.white)),
          ],
        ),
        content: Text(
          "Detection confidence was ${(confidence * 100).toStringAsFixed(1)}%.\n\n"
          "Low confidence. Please capture another image in good lighting.",
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: kEmerald,
            ),
            onPressed: () {
              Navigator.pop(ctx);
              _pickImage(ImageSource.camera);
            },
            child: const Text("Retake Photo", style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showSnackBar(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.redAccent),
    );
  }

  void _toggleSpeech() async {
    if (_advisoryHindi == null) return;
    if (_isSpeaking) {
      await TTSService.stop();
      setState(() => _isSpeaking = false);
    } else {
      setState(() => _isSpeaking = true);
      await TTSService.speak(_advisoryHindi!);
      setState(() => _isSpeaking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("YOLO Disease Detection", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview Container
            Container(
              height: 220,
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: kEmerald.withValues(alpha: 0.3), width: 1.5),
              ),
              child: _selectedImage != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(15),
                      child: Image.file(_selectedImage!, fit: BoxFit.cover),
                    )
                  : const Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.center_focus_weak_rounded, size: 64, color: kEmerald),
                        SizedBox(height: 12),
                        Text(
                          "Capture or upload a crop leaf image",
                          style: TextStyle(color: Colors.white70, fontSize: 14),
                        ),
                      ],
                    ),
            ),
            const SizedBox(height: 16),

            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: kEmerald,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt, color: Colors.white),
                    label: const Text("Take Photo", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: kEmerald),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library, color: kEmerald),
                    label: const Text("Gallery", style: TextStyle(color: kEmerald, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            if (_isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(24.0),
                  child: CircularProgressIndicator(color: kEmerald),
                ),
              ),

            if (!_isLoading && _scanResult != null) ...[
              // Disease Result Card
              _buildDiseaseResultCard(),
              const SizedBox(height: 16),

              // Hindi Voice Advisory Card
              if (_advisoryHindi != null) _buildHindiAdvisoryCard(),
              const SizedBox(height: 16),

              // Smart Action Plan Cards
              if (_actionPlan != null) _buildActionPlanSection(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDiseaseResultCard() {
    final name = _scanResult!["disease_name"] ?? _scanResult!["label"] ?? "Unknown";
    final conf = ((_scanResult!["confidence"] ?? 0.0) * 100).toStringAsFixed(1);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: kEmerald.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  name,
                  style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: kEmerald.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: kEmerald),
                ),
                child: Text(
                  "$conf% Match",
                  style: const TextStyle(color: kEmerald, fontWeight: FontWeight.bold, fontSize: 12),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHindiAdvisoryCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "AI Crop Doctor Advice (हिंदी)",
                style: TextStyle(color: kEmerald, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              IconButton(
                icon: Icon(
                  _isSpeaking ? Icons.stop_circle : Icons.volume_up_rounded,
                  color: kEmerald,
                  size: 28,
                ),
                onPressed: _toggleSpeech,
              ),
            ],
          ),
          const Divider(color: Colors.white12),
          Text(
            _advisoryHindi!,
            style: const TextStyle(color: Colors.white70, fontSize: 14, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _buildActionPlanSection() {
    final today = List<String>.from(_actionPlan!["today"] ?? []);
    final next3 = List<String>.from(_actionPlan!["next_3_days"] ?? []);
    final nextWeek = List<String>.from(_actionPlan!["next_week"] ?? []);
    final warning = List<String>.from(_actionPlan!["warning_signs"] ?? []);
    final recovery = _actionPlan!["expected_recovery"] as String? ?? "10-14 Days";

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Smart Action Plan",
          style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),

        // Expected Recovery Banner
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blueAccent.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blueAccent),
          ),
          child: Row(
            children: [
              const Icon(Icons.timer_outlined, color: Colors.blueAccent),
              const SizedBox(width: 10),
              Text(
                "Expected Recovery Time: $recovery",
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Today's Action Plan
        _buildPlanCard("Today's Action Plan", today, Icons.today, kEmerald),
        const SizedBox(height: 10),

        // Next 3 Days
        _buildPlanCard("Next 3 Days", next3, Icons.calendar_view_week, Colors.amber),
        const SizedBox(height: 10),

        // Next Week
        _buildPlanCard("Next Week", nextWeek, Icons.date_range, Colors.cyan),
        const SizedBox(height: 10),

        // Warning Signs
        if (warning.isNotEmpty)
          _buildPlanCard("Warning Signs", warning, Icons.warning_rounded, Colors.redAccent),
      ],
    );
  }

  Widget _buildPlanCard(String title, List<String> items, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 15),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...items.map(
            (item) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.check_circle_outline, color: color.withValues(alpha: 0.7), size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item,
                      style: const TextStyle(color: Colors.white70, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}