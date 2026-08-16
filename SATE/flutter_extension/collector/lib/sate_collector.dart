import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as path;

import 'src/event.dart';

/// Classifies errors into SATE severity tiers (FATAL, ANR, E+, E)
class ErrorClassifier {
  static String classifyError(dynamic error, StackTrace? stack) {
    final errorStr = error.toString().toLowerCase();

    // FATAL: Unhandled runtime crashes
    if (error is TypeError ||
        error is NoSuchMethodError ||
        error is AssertionError ||
        errorStr.contains('outofmemory') ||
        errorStr.contains('stackoverflow') ||
        errorStr.contains('unhandled exception') ||
        errorStr.contains('rangeerror') ||
        errorStr.contains('argumenterror') ||
        errorStr.contains('stateerror')) {
      return 'FATAL';
    }

    // ANR: Application Not Responding (timeout-related)
    if (errorStr.contains('timeout') ||
        errorStr.contains('timedout') ||
        errorStr.contains('deadline') ||
        (error is PlatformException && errorStr.contains('timeout'))) {
      return 'ANR';
    }

    // E+: System/framework-level errors
    if (error is FlutterError ||
        error is PlatformException ||
        error is MissingPluginException ||
        errorStr.contains('renderflex overflowed') ||
        errorStr.contains('scaffold') ||
        errorStr.contains('material') ||
        errorStr.contains('widget') ||
        errorStr.contains('build') ||
        errorStr.contains('layout') ||
        errorStr.contains('rendering')) {
      return 'E+';
    }

    // E: Application-level errors (default)
    return 'E';
  }
}

/// Main collector class for SATE Flutter integration
class SateCollector {
  static final SateCollector _instance = SateCollector._internal();
  factory SateCollector() => _instance;
  SateCollector._internal();

  static SateCollector get instance => _instance;

  final List<SateEvent> _events = [];
  String? _outputDir;
  bool _isRunning = false;
  String? _packageName;
  String? _tag;
  bool _verbose = false;
  int? _startTime;

  // Time-series coverage
  Timer? _coverageTimer;
  int _coverageInterval = 30;
  bool _timeSeriesEnabled = false;

  // Coverage data from lcov.info
  String? _lcovPath;

  /// Start the collector
  void start({
    required String outputDir,
    required String packageName,
    required String tag,
    bool verbose = false,
    bool enableTimeSeries = false,
    int coverageInterval = 30,
    String? lcovPath,
  }) {
    _verbose = verbose;
    _timeSeriesEnabled = enableTimeSeries;
    _coverageInterval = coverageInterval;
    _lcovPath = lcovPath;
    _startTime = DateTime.now().millisecondsSinceEpoch ~/ 1000;

    if (_isRunning) {
      _log('⚠️ SateCollector is already running', level: 'WARNING');
      return;
    }

    _outputDir = outputDir;
    _packageName = packageName;
    _tag = tag;
    _isRunning = true;

    _log('✅ SateCollector started');
    _log('   Output: $_outputDir');
    _log('   Package: $_packageName');
    _log('   Tag: $_tag');
    _log('   Verbose: $_verbose');
    _log('   Time-series: $_timeSeriesEnabled');
    _log('   Coverage Interval: $_coverageInterval seconds');

    // Create output directory
    try {
      final dir = Directory(_outputDir!);
      if (!dir.existsSync()) {
        dir.createSync(recursive: true);
        _log('   Created output directory');
      }
    } catch (e) {
      _log('❌ Failed to create output directory: $e', level: 'ERROR');
      return;
    }

    // Register error handler with dynamic severity classification
    FlutterError.onError = (FlutterErrorDetails details) {
      final severity = ErrorClassifier.classifyError(
        details.exception,
        details.stack,
      );
      _log('Flutter error caught: ${details.exception} [severity: $severity]',
          level: 'ERROR');
      _recordFault(
        severity: severity,
        exception: details.exception.runtimeType.toString(),
        message: details.exceptionAsString(),
        stackTrace: details.stack?.toString() ?? '',
        tag: 'Flutter',
      );
    };

    PlatformDispatcher.instance.onError = (error, stack) {
      final severity = ErrorClassifier.classifyError(error, stack);
      _log('Platform error caught: $error [severity: $severity]',
          level: 'ERROR');
      _recordFault(
        severity: severity,
        exception: error.runtimeType.toString(),
        message: error.toString(),
        stackTrace: stack.toString(),
        tag: 'Platform',
      );
      return true;
    };

    _log('   Event handlers registered');

    // Start time-series coverage collection
    if (_timeSeriesEnabled) {
      _startTimeSeriesCoverage();
    }
  }

  /// Stop the collector and save data
  Future<void> stop() async {
    if (!_isRunning) {
      _log('⚠️ SateCollector is not running', level: 'WARNING');
      return;
    }

    // Stop time-series coverage
    if (_timeSeriesEnabled) {
      _stopTimeSeriesCoverage();
    }

    _isRunning = false;
    _log('📝 Stopping SateCollector...');

    // Calculate time metrics
    final startTime = _startTime ?? DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final endTime = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final duration = endTime - startTime;

    // Build the output JSON
    final output = {
      'metadata': {
        'package': _packageName,
        'tag': _tag,
        'start_time': startTime,
        'end_time': endTime,
        'duration': duration,
        'event_count': _events.length,
        'time_series_enabled': _timeSeriesEnabled,
        'coverage_interval': _coverageInterval,
      },
      'events': _events.map((e) => e.toJson()).toList(),
    };

    // Write to file
    try {
      final filePath = path.join(_outputDir!, 'collector_output.json');
      final file = File(filePath);
      await file.writeAsString(jsonEncode(output));

      _log('✅ SateCollector stopped');
      _log('   Events collected: ${_events.length}');
      _log('   Output file: $filePath');
      _log('   File size: ${await file.length()} bytes');
      _log('   Duration: $duration seconds');
    } catch (e) {
      _log('❌ Failed to write output: $e', level: 'ERROR');
    }

    _events.clear();
  }

  // Time-series coverage methods
  void _startTimeSeriesCoverage() {
    _log('📊 Starting time-series coverage collection (interval: $_coverageInterval seconds)');

    // Record initial coverage immediately
    _captureCoverageSnapshot();

    // Start periodic timer
    _coverageTimer = Timer.periodic(
      Duration(seconds: _coverageInterval),
      (timer) => _captureCoverageSnapshot(),
    );
  }

  void _stopTimeSeriesCoverage() {
    _coverageTimer?.cancel();
    _coverageTimer = null;
    _log('📊 Time-series coverage collection stopped');
  }

  void _captureCoverageSnapshot() {
    if (!_isRunning) return;

    _log('📊 Capturing coverage snapshot...');

    // If lcov path is provided, parse it
    if (_lcovPath != null && File(_lcovPath!).existsSync()) {
      try {
        final coverage = _parseLcovFile(_lcovPath!);
        _recordCoverageSnapshot(coverage);
        _log('   ✅ Snapshot captured');
      } catch (e) {
        _log('   ❌ Failed to parse lcov: $e', level: 'ERROR');
      }
    } else {
      _recordCoverageSnapshot({});
      _log('   ⚠️ No lcov file available, recording baseline coverage snapshot',
          level: 'WARNING');
    }
  }

  Map<String, Map<String, double>> _parseLcovFile(String path) {
    final file = File(path);
    final lines = file.readAsLinesSync();

    Map<String, Map<String, double>> coverage = {};
    String currentFile = '';
    int covered = 0;
    int total = 0;

    for (var line in lines) {
      if (line.startsWith('SF:')) {
        currentFile = line.substring(3);
        covered = 0;
        total = 0;
      } else if (line.startsWith('DA:')) {
        total++;
        final parts = line.substring(3).split(',');
        if (parts.length == 2 && parts[1] != '0') {
          covered++;
        }
      } else if (line.startsWith('end_of_record')) {
        if (currentFile.isNotEmpty) {
          final fileName = currentFile.split('/').last;
          coverage[fileName] = {
            'covered': covered.toDouble(),
            'total': total.toDouble(),
            'rate': total > 0 ? covered / total : 0.0,
          };
        }
      }
    }

    return coverage;
  }

  void _recordCoverageSnapshot(Map<String, Map<String, double>> coverage) {
    if (!_isRunning) return;

    // Aggregate coverage by metric
    final metrics = {
      'LINE': {'covered': 0.0, 'total': 0.0},
      'METHOD': {'covered': 0.0, 'total': 0.0},
      'BRANCH': {'covered': 0.0, 'total': 0.0},
      'CLASS': {'covered': 0.0, 'total': 0.0},
      'INSTRUCTION': {'covered': 0.0, 'total': 0.0},
      'COMPLEXITY': {'covered': 0.0, 'total': 0.0},
      'ACTIVITY': {'covered': 0.0, 'total': 0.0},
    };

    for (var entry in coverage.entries) {
      final data = entry.value;
      for (var metric in metrics.keys) {
        metrics[metric]!['covered'] =
            (metrics[metric]!['covered'] ?? 0) + (data['covered'] ?? 0);
        metrics[metric]!['total'] =
            (metrics[metric]!['total'] ?? 0) + (data['total'] ?? 0);
      }
    }

    // Record each metric as a CoverageEvent with timestamp
    final timestamp = DateTime.now().millisecondsSinceEpoch ~/ 1000;

    for (var entry in metrics.entries) {
      final metric = entry.key;
      final data = entry.value;
      final covered = data['covered'] ?? 0;
      final total = data['total'] ?? 0;
      final rate = total > 0 ? covered / total : 0.0;

      final event = CoverageEvent(
        metric: metric,
        covered: covered,
        total: total,
        rate: rate,
        timestamp: timestamp,
      );
      _events.add(event);
    }

    _log('   📊 Recorded ${metrics.keys.length} metrics at timestamp $timestamp');
  }

  /// Record a screen navigation
  void recordScreen(String screenName, {String? previousScreen}) {
    if (!_isRunning) {
      _log('⚠️ Attempted to record screen while collector not running',
          level: 'WARNING');
      return;
    }

    final event = ScreenEvent(
      screenName: screenName,
      previousScreen: previousScreen,
      timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
    );
    _events.add(event);
    _log('📍 Screen recorded: $screenName${previousScreen != null ? " (from $previousScreen)" : ""}');
  }

  /// Record a fault/exception with dynamic severity
  void recordFault({
    required String severity,
    required String exception,
    required String message,
    required String stackTrace,
    String? tag,
  }) {
    _recordFault(
      severity: severity,
      exception: exception,
      message: message,
      stackTrace: stackTrace,
      tag: tag,
    );
  }

  void _recordFault({
    required String severity,
    required String exception,
    required String message,
    required String stackTrace,
    String? tag,
  }) {
    if (!_isRunning) {
      _log('⚠️ Attempted to record fault while collector not running',
          level: 'WARNING');
      return;
    }

    final event = FaultEvent(
      severity: severity,
      exception: exception,
      message: message,
      stackTrace: stackTrace,
      tag: tag,
      timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
    );
    _events.add(event);
    _log(
        '⚠️ Fault recorded: [$severity] $exception - ${message.substring(0, message.length > 50 ? 50 : message.length)}...');
  }

  /// Record coverage data
  void recordCoverage({
    required String metric,
    required double covered,
    required double total,
  }) {
    if (!_isRunning) {
      _log('⚠️ Attempted to record coverage while collector not running',
          level: 'WARNING');
      return;
    }

    final rate = total > 0 ? covered / total : 0.0;
    final event = CoverageEvent(
      metric: metric,
      covered: covered,
      total: total,
      rate: rate,
      timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
    );
    _events.add(event);
    _log(
        '📊 Coverage recorded: $metric = ${(rate * 100).toStringAsFixed(1)}% ($covered/$total)');
  }

  /// Get all collected events
  List<SateEvent> get events => List.unmodifiable(_events);

  /// Check if collector is running
  bool get isRunning => _isRunning;

  void _log(String message, {String level = 'INFO'}) {
    if (_verbose || level == 'ERROR' || level == 'WARNING') {
      final timestamp = DateTime.now().toIso8601String();
      print('[$timestamp] [$level] [SateCollector] $message');
    }
  }
}

/// Route observer for automatic screen tracking
class SateRouteObserver extends RouteObserver<PageRoute<dynamic>> {
  String? _currentScreen;

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);

    final screenName = _getScreenName(route);
    if (screenName != null) {
      SateCollector.instance.recordScreen(
        screenName,
        previousScreen: _currentScreen,
      );
      _currentScreen = screenName;
    }
  }

  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) {
    super.didReplace(newRoute: newRoute, oldRoute: oldRoute);

    final screenName = _getScreenName(newRoute);
    if (screenName != null) {
      SateCollector.instance.recordScreen(
        screenName,
        previousScreen: _currentScreen,
      );
      _currentScreen = screenName;
    }
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPop(route, previousRoute);

    final screenName = _getScreenName(previousRoute);
    if (screenName != null) {
      SateCollector.instance.recordScreen(
        screenName,
        previousScreen: _currentScreen,
      );
      _currentScreen = screenName;
    }
  }

  String? _getScreenName(Route<dynamic>? route) {
    if (route == null) return null;
    if (route is PageRoute) {
      return route.settings.name ?? route.runtimeType.toString();
    }
    return route.runtimeType.toString();
  }
}