import 'package:flutter/material.dart';
import 'package:flutter_extension_collector/sate_collector.dart';

void main() {
  // Start the collector with time-series enabled
  SateCollector.instance.start(
    outputDir: './collector_output',
    packageName: 'com.example.demo_app',
    tag: 'demo-run-1',
    verbose: true,
    enableTimeSeries: true,
    coverageInterval: 10, // Capture every 10 seconds
  );

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SATE Demo',
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
      appBar: AppBar(title: const Text('Home')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Welcome to SATE Demo'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/details');
              },
              child: const Text('Go to Details'),
            ),
            const SizedBox(height: 20),
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
                    tag: 'Demo',
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Exception captured!')),
                  );
                }
              },
              child: const Text('Trigger Exception'),
            ),
            const SizedBox(height: 20),
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
      appBar: AppBar(title: const Text('Details')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
          },
          child: const Text('Go Back'),
        ),
      ),
    );
  }
}