import 'package:flutter/material.dart';

/// SmartEdge AgriGuardian - App Theme
/// Dark Green Farming Theme - Clean & Professional

class AppColors {
  // Primary Greens
  static const Color primaryGreen = Color(0xFF2E7D32);
  static const Color darkGreen = Color(0xFF1B5E20);
  static const Color lightGreen = Color(0xFF4CAF50);
  static const Color accentGreen = Color(0xFF81C784);

  // Background
  static const Color background = Color(0xFF121A12);
  static const Color surface = Color(0xFF1E2A1E);
  static const Color cardBackground = Color(0xFF243524);

  // Status Colors
  static const Color healthy = Color(0xFF4CAF50);   // Green
  static const Color warning = Color(0xFFFFC107);   // Yellow
  static const Color danger = Color(0xFFE53935);    // Red

  // Text
  static const Color textPrimary = Color(0xFFF1F8F1);
  static const Color textSecondary = Color(0xFFA5C4A5);
  static const Color textMuted = Color(0xFF6B8A6B);

  // Utility
  static const Color divider = Color(0xFF2E3E2E);
}

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.background,
      primaryColor: AppColors.primaryGreen,
      fontFamily: 'Roboto',

      colorScheme: const ColorScheme.dark(
        primary: AppColors.primaryGreen,
        secondary: AppColors.lightGreen,
        surface: AppColors.surface,
        error: AppColors.danger,
      ),

      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.background,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 22,
          fontWeight: FontWeight.bold,
        ),
        iconTheme: IconThemeData(color: AppColors.textPrimary),
      ),

      cardTheme: CardThemeData(
        color: AppColors.cardBackground,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        margin: EdgeInsets.zero,
      ),

      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.surface,
        selectedItemColor: AppColors.lightGreen,
        unselectedItemColor: AppColors.textMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primaryGreen,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),

      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: AppColors.lightGreen,
        foregroundColor: Colors.white,
      ),

      textTheme: const TextTheme(
        headlineLarge: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 28,
          fontWeight: FontWeight.bold,
        ),
        headlineMedium: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 22,
          fontWeight: FontWeight.bold,
        ),
        titleLarge: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 16,
        ),
        bodyMedium: TextStyle(
          color: AppColors.textSecondary,
          fontSize: 14,
        ),
        bodySmall: TextStyle(
          color: AppColors.textMuted,
          fontSize: 12,
        ),
      ),

      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 1,
      ),
    );
  }

  /// Helper to get color based on health score (0-100)
  static Color getHealthColor(double score) {
    if (score >= 70) return AppColors.healthy;
    if (score >= 40) return AppColors.warning;
    return AppColors.danger;
  }
}