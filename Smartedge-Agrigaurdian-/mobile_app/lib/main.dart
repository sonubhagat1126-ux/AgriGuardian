import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'features/home/home_screen.dart';
import 'features/scan/scan_screen.dart';
import 'features/farm_map/farm_map_screen.dart';
import 'features/voice/voice_screen.dart';
import 'features/analytics/analytics_screen.dart';

void main() {
  runApp(const AgriGuardianApp());
}

class AgriGuardianApp extends StatelessWidget {
  const AgriGuardianApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartEdge AgriGuardian',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainNavigation(),
    );
  }
}

/// Main Navigation - Bottom Nav Bar with 5 tabs
/// Home | Map | Scan | Voice | Analytics
class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  // Lazy list of screens - built once
  final List<Widget> _screens = const [
    HomeScreen(),
    FarmMapScreen(),
    ScanScreen(),
    VoiceScreen(),
    AnalyticsScreen(),
  ];

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_rounded),
            label: 'Map',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.camera_alt_rounded),
            label: 'Scan',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.mic_rounded),
            label: 'Voice',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.bar_chart_rounded),
            label: 'Analytics',
          ),
        ],
      ),
    );
  }
}