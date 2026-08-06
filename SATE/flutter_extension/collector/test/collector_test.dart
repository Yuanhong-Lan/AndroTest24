import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_extension_collector/sate_collector.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  tearDown(() async {
    if (SateCollector.instance.isRunning) {
      await SateCollector.instance.stop();
    }
  });

  test('SateCollector records events', () async {
    final collector = SateCollector.instance;
    
    collector.start(
      outputDir: './test_output',
      packageName: 'test.app',
      tag: 'test-run-1',
      enableTimeSeries: false,
      verbose: false,
    );
    
    collector.recordScreen('HomeScreen');
    collector.recordCoverage(metric: 'LINE', covered: 50, total: 100);
    
    expect(collector.events.length, 2);
    expect(collector.events[0].type, 'screen');
    expect(collector.events[1].type, 'coverage');
    
    // Check that time-series didn't add extra events
    final coverageEvents = collector.events.where((e) => e.type == 'coverage').toList();
    expect(coverageEvents.length, 1);

    await collector.stop();
  });

  test('SateCollector time-series records multiple snapshots', () async {
    final collector = SateCollector.instance;
    
    collector.start(
      outputDir: './test_output',
      packageName: 'test.app',
      tag: 'test-run-2',
      enableTimeSeries: true,
      coverageInterval: 1, // 1 second for testing
      verbose: false,
    );
    
    // Wait for 2 intervals
    await Future.delayed(const Duration(seconds: 3));
    
    final coverageEvents = List.of(collector.events.where((e) => e.type == 'coverage'));
    
    await collector.stop();
    
    expect(coverageEvents.length >= 2, true); // at least initial + 2 intervals
  });
}
