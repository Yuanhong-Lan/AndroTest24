# Flutter Integration for SATE Framework

## Overview

This extension enables SATE to evaluate Flutter applications by collecting:

- **Coverage data**: Widget, screen, line, method, branch, class, instruction, complexity, and activity coverage
- **Fault detection**: Exceptions, ANRs, and crashes classified by severity (FATAL, ANR, E+, E)
- **Screen navigation**: Automatic tracking of screen transitions via RouteObserver

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUTTER APPLICATION                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    SateCollector                            │ │
│  │  • Records coverage metrics                                │ │
│  │  • Captures faults/exceptions                              │ │
│  │  • Tracks screen navigation                                │ │
│  │  • Exports JSON data                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    collector_output.json
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PYTHON BRIDGE                              │
│  • Converts JSON → SATE .npy format                            │
│  • Generates SATE-compatible logcat files                      │
│  • Creates placeholder files (4-file check)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    SATE-ready data files
                    (.npy + .logcat + placeholders)
```

## Prerequisites

- **Flutter SDK**: >=3.0.0
- **Python**: >=3.7
- **Dependencies**: `pip install -r requirements.txt`

## Quick Start Guide

### Step 1: Add the Collector to Your Flutter App

**Option A: Local Path (Recommended for testing)**

```yaml
# pubspec.yaml
dependencies:
  flutter_extension_collector:
    path: ../path/to/AndroTest24/SATE/flutter_extension/collector
```

**Option B: Git Dependency**

```yaml
# pubspec.yaml
dependencies:
  flutter_extension_collector:
    git:
      url: https://github.com/Yuanhong-Lan/AndroTest24.git
      path: SATE/flutter_extension/collector
```

### Step 2: Initialize the Collector

```dart
// main.dart
import 'package:flutter/material.dart';
import 'package:flutter_extension_collector/sate_collector.dart';

void main() {
  // Start the collector before running the app
  SateCollector.instance.start(
    outputDir: './collector_output',      // Where to save data
    packageName: 'com.example.myapp',      // Your app's package name
    tag: 'test-run-1',                     // Unique identifier for this test run
    enableTimeSeries: true,               // Enable time-series collection
    coverageInterval: 30,                 // Capture every 30 seconds
  );

  runApp(const MyApp());
}
```

### Step 3: Add Screen Tracking

```dart
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My App',
      // ⬇️ Add this to automatically track screen navigation
      navigatorObservers: [SateRouteObserver()],
      home: const HomeScreen(),
    );
  }
}
```

### Step 4: Record Coverage Manually (Optional)

```dart
// During test execution
SateCollector.instance.recordCoverage(
  metric: 'LINE',
  covered: 45,
  total: 100,
);

SateCollector.instance.recordCoverage(
  metric: 'METHOD',
  covered: 8,
  total: 20,
);
```

### Step 5: Record Exceptions

```dart
try {
  // Some code that might throw
} catch (e, stackTrace) {
  SateCollector.instance.recordFault(
    severity: 'E',
    exception: e.runtimeType.toString(),
    message: e.toString(),
    stackTrace: stackTrace.toString(),
    tag: 'MyFeature',  // Optional: identifier for the source
  );
}
```

### Step 6: Stop the Collector

```dart
// When tests are complete (e.g., in tearDown)
await SateCollector.instance.stop();
```

### Step 7: Convert to SATE Format

```bash
cd SATE/flutter_extension/bridge

# Install Python dependencies
pip install -r requirements.txt

# Convert collector output to SATE format
python bridge.py \
  --json-input /path/to/collector_output.json \
  --output-dir /path/to/sate_data \
  --tag test-run-1 \
  --package com.example.myapp
```

## Time-Series Coverage

### Overview

The Flutter SATE extension supports time-series coverage collection, allowing you to track coverage metrics at regular intervals during test execution. This is essential for SATE's statistical analysis, which expects coverage data over time.

### Configuration

Enable time-series coverage when starting the collector:

```dart
SateCollector.instance.start(
  outputDir: './collector_output',
  packageName: 'com.example.myapp',
  tag: 'test-run-1',
  enableTimeSeries: true,     // Enable time-series collection
  coverageInterval: 30,       // Capture every 30 seconds
  verbose: true,              // See progress logs
);
```

### How It Works

1. **Initial Snapshot**: Coverage is captured immediately when the collector starts
2. **Periodic Snapshots**: Coverage is captured at the configured interval
3. **Event Recording**: Each snapshot is recorded as a `CoverageEvent` with a timestamp
4. **Data Export**: All snapshots are included in `collector_output.json`
5. **SATE Conversion**: The Python bridge converts time-series data to SATE's expected format

### Output Format

Each coverage snapshot includes:
- `metric`: The coverage metric (LINE, METHOD, BRANCH, etc.)
- `covered`: Number of covered items
- `total`: Total number of items
- `rate`: Coverage rate (`covered / total`)
- `timestamp`: Unix timestamp when snapshot was captured

### Example Output

```json
{
  "events": [
    {
      "type": "coverage",
      "timestamp": 1700000000,
      "data": {
        "metric": "LINE",
        "covered": 45,
        "total": 100,
        "rate": 0.45
      }
    },
    {
      "type": "coverage",
      "timestamp": 1700000030,
      "data": {
        "metric": "LINE",
        "covered": 55,
        "total": 100,
        "rate": 0.55
      }
    }
  ]
}
```

### SATE Compatibility

The time-series data is fully compatible with SATE's expected input format. Each metric contains multiple `CoverageItem` entries with different timestamps, allowing SATE to perform time-based statistical analysis.

### Performance Considerations

- **Interval Selection**: Shorter intervals provide more data points but increase overhead
- **Recommended Interval**: 30 seconds balances data granularity with performance
- **Test Duration**: 3 hours (10,800 seconds) is the standard SATE test duration
- **Data Points**: At 30-second intervals, expect ~360 data points per metric

### Use Cases

- **Research Studies**: Track coverage evolution over time
- **Performance Analysis**: Identify when coverage stabilizes
- **Tool Comparison**: Compare coverage growth rates between testing tools
- **Convergence Analysis**: Determine when additional testing stops improving coverage

## Complete Example

### Full Flutter App with Collector

Create `lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_extension_collector/sate_collector.dart';

void main() {
  // Initialize collector with time-series enabled
  SateCollector.instance.start(
    outputDir: './collector_output',
    packageName: 'com.example.demo_app',
    tag: 'demo-run-1',
    enableTimeSeries: true,
    coverageInterval: 10,
    verbose: true,
  );

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SATE Demo App',
      navigatorObservers: [SateRouteObserver()],
      routes: {
        '/': (context) => const HomeScreen(),
        '/details': (context) => const DetailsScreen(),
      },
      initialRoute: '/',
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Home Screen')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Welcome to SATE Demo'),
            const SizedBox(height: 20),
            
            // Navigate to details screen
            ElevatedButton(
              onPressed: () => Navigator.pushNamed(context, '/details'),
              child: const Text('Go to Details'),
            ),
            
            const SizedBox(height: 20),
            
            // Simulate an exception
            ElevatedButton(
              onPressed: () {
                try {
                  throw Exception('Demo exception for SATE');
                } catch (e, stack) {
                  SateCollector.instance.recordFault(
                    severity: 'E',
                    exception: e.runtimeType.toString(),
                    message: e.toString(),
                    stackTrace: stack.toString(),
                    tag: 'DemoButton',
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Exception captured!')),
                  );
                }
              },
              child: const Text('Trigger Exception'),
            ),
            
            const SizedBox(height: 20),
            
            // Record coverage
            ElevatedButton(
              onPressed: () {
                SateCollector.instance.recordCoverage(
                  metric: 'LINE',
                  covered: 45,
                  total: 100,
                );
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Coverage recorded!')),
                );
              },
              child: const Text('Record Coverage'),
            ),
          ],
        ),
      ),
    );
  }
}

class DetailsScreen extends StatelessWidget {
  const DetailsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Details Screen')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('This is the details screen'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Running the Example

```bash
# 1. Go to the example directory
cd SATE/flutter_extension/collector/example

# 2. Run the app
flutter run

# 3. Interact with the app (tap buttons, navigate)

# 4. After testing, stop the app (Ctrl+C)

# 5. Check the output
cat collector_output/collector_output.json

# 6. Convert to SATE format
cd ../../bridge
python bridge.py \
  --json-input ../collector/example/collector_output/collector_output.json \
  --output-dir ./sate_output \
  --tag demo-run-1 \
  --package com.example.demo_app

# 7. Verify output files
ls -la ./sate_output/com.example.demo_app/demo-run-1/
# Should show 4 files:
# - demo-run-1_Jacoco.npy
# - demo-run-1_placeholder_1.txt
# - demo-run-1_placeholder_2.txt
# - demo-run-1_placeholder_3.txt
```

## API Reference

### SateCollector

| Method | Description | Parameters |
|--------|-------------|------------|
| `start()` | Initialize the collector | `outputDir`: String (required)<br>`packageName`: String (required)<br>`tag`: String (required)<br>`enableTimeSeries`: bool (optional)<br>`coverageInterval`: int (optional)<br>`lcovPath`: String? (optional) |
| `stop()` | Stop and save data | Returns `Future<void>` |
| `recordScreen()` | Record screen navigation | `screenName`: String<br>`previousScreen`: String? (optional) |
| `recordFault()` | Record an exception/fault | `severity`: String ('FATAL', 'ANR', 'E+', 'E')<br>`exception`: String<br>`message`: String<br>`stackTrace`: String<br>`tag`: String? (optional) |
| `recordCoverage()` | Record coverage metric | `metric`: String ('LINE', 'METHOD', 'BRANCH', etc.)<br>`covered`: double<br>`total`: double |
| `events` | Get all collected events | Returns `List<SateEvent>` |
| `isRunning` | Check if collector is active | Returns `bool` |

### SateRouteObserver

Automatically tracks screen navigation when added to `navigatorObservers`.

### SateEvent Types

| Type | Description | Data Fields |
|------|-------------|-------------|
| `coverage` | Coverage metric record | `metric`, `covered`, `total`, `rate` |
| `fault` | Exception/fault record | `severity`, `exception`, `message`, `stackTrace`, `tag` |
| `screen` | Screen navigation record | `screenName`, `previousScreen` |

## Fault Classification

Follows ASE24 paper tiers:

| Tier | Description | Severity Value |
|------|-------------|----------------|
| **FATAL** | Unhandled runtime crashes | `FATAL` |
| **ANR** | Application Not Responding | `ANR` |
| **E+** | System/framework-level errors (matches `E_PLUS_LIST` tags) | `E+` |
| **E** | All application-level errors | `E` |

### E_PLUS_LIST Tags (System-level errors)

When a fault has tag matching any of these, it's classified as E+:
- AndroidRuntime
- CrashAnrDetector
- ActivityManager
- SQLiteDatabase
- WindowManager
- ActivityThread
- Parcel

## Output Format

### collector_output.json

```json
{
  "metadata": {
    "package": "com.example.myapp",
    "tag": "test-run-1",
    "start_time": 1700000000,
    "end_time": 1700010800,
    "time_series_enabled": true,
    "coverage_interval": 30
  },
  "events": [
    {
      "type": "screen",
      "timestamp": 1700000010,
      "data": {
        "screenName": "HomeScreen",
        "previousScreen": null
      }
    },
    {
      "type": "fault",
      "timestamp": 1700000100,
      "data": {
        "severity": "E",
        "exception": "Exception",
        "message": "Demo exception for SATE",
        "stackTrace": "...",
        "tag": "DemoButton"
      }
    },
    {
      "type": "coverage",
      "timestamp": 1700000200,
      "data": {
        "metric": "LINE",
        "covered": 45,
        "total": 100,
        "rate": 0.45
      }
    }
  ]
}
```

## Troubleshooting

### Issue: Collector not recording events

**Solution:**
```dart
// Make sure you started the collector
if (!SateCollector.instance.isRunning) {
  SateCollector.instance.start(...);
}
```

### Issue: RouteObserver not tracking screens

**Solution:**
```dart
// Make sure it's added to navigatorObservers
MaterialApp(
  navigatorObservers: [SateRouteObserver()],
  // ...
)
```

### Issue: Python bridge fails

**Solution:**
```bash
# Check dependencies
pip install -r requirements.txt

# Check input file exists
ls -la collector_output.json

# Run with --help
python bridge.py --help
```

## Next Steps

After implementing the collector:

1. **Run tests** with `flutter test --coverage`
2. **Convert data** using the Python bridge
3. **Feed data into SATE** for statistical analysis
4. **Iterate** based on results

## Contributing

Found a bug or want to add a feature?
1. Fork the repository
2. Create a feature branch
3. Submit a PR

## License

This extension is part of AndroTest24 and follows the same MIT license.
