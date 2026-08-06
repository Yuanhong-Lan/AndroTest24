import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_extension_collector/sate_collector.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('SateCollector records events', () {
    final collector = SateCollector.instance;
    
    collector.start(
      outputDir: './test_output',
      packageName: 'test.app',
      tag: 'test-run',
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
  });

  test('SateCollector time-series records multiple snapshots', () async {
    final collector = SateCollector.instance;
    
    collector.start(
      outputDir: './test_output',
      packageName: 'test.app',
      tag: 'test-run',
      enableTimeSeries: true,
      coverageInterval: 1, // 1 second for testing
      verbose: false,
    );
    
    // Wait for 2 intervals
    await Future.delayed(const Duration(seconds: 3));
    
    await collector.stop();
    
    final coverageEvents = collector.events.where((e) => e.type == 'coverage').toList();
    expect(coverageEvents.length >= 2, true); // at least initial + 2 intervals
  });
}
