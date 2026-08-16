import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_extension_collector/sate_collector.dart';
import 'package:flutter/foundation.dart';

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
      coverageInterval: 1,
      verbose: false,
    );

    await Future.delayed(const Duration(seconds: 3));

    final coverageEvents = List.of(collector.events.where((e) => e.type == 'coverage'));

    await collector.stop();

    expect(coverageEvents.length >= 2, true);
  });

  test('ErrorClassifier correctly classifies errors', () {
    // FATAL
    expect(ErrorClassifier.classifyError(TypeError(), null), 'FATAL');
    expect(ErrorClassifier.classifyError(NoSuchMethodError.withInvocation(null, Invocation.getter(#test)), null), 'FATAL');
    expect(ErrorClassifier.classifyError(AssertionError(), null), 'FATAL');

    // ANR
    expect(ErrorClassifier.classifyError(Exception('timeout'), null), 'ANR');
    expect(ErrorClassifier.classifyError(Exception('TimedOut'), null), 'ANR');

    // E+
    expect(ErrorClassifier.classifyError(FlutterError(''), null), 'E+');

    // E (default)
    expect(ErrorClassifier.classifyError(Exception('regular error'), null), 'E');
  });
}
