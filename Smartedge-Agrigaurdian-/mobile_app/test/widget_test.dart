import 'package:flutter_test/flutter_test.dart';
import 'package:smartedge_agriguardian/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const AgriGuardianApp());
    expect(find.byType(AgriGuardianApp), findsOneWidget);
  });
}
