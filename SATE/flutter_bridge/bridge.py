import json
from pathlib import Path
import numpy as np
import click

def convert_to_sate_coverage(json_data):
    metric_keys = ['INSTRUCTION', 'BRANCH', 'LINE', 'COMPLEXITY', 'METHOD', 'CLASS', 'ACTIVITY']
    sate_coverage = {}
    events = json_data.get('events', [])
    coverage_events = [e for e in events if e.get('type') == 'coverage']
    coverage_by_metric = {}
    for event in coverage_events:
        data = event.get('data', {})
        metric = data.get('metric', 'UNKNOWN')
        if metric not in coverage_by_metric:
            coverage_by_metric[metric] = []
        coverage_by_metric[metric].append({
            'time': event.get('timestamp', 0),
            'detail': {
                'covered': float(data.get('covered', 0)),
                'total': float(data.get('total', 0)),
                'rate': float(data.get('rate', 0))
            }
        })
    for key in metric_keys:
        sate_coverage[key] = coverage_by_metric.get(key, [])
    return sate_coverage

def generate_fault_key(fault, app_name):
    data = fault.get('data', {})
    severity = data.get('severity', 'E')
    exc = data.get('exception', 'Unknown')
    tag = data.get('tag', 'unknown')
    msg = data.get('message', 'No reason')
    if severity == 'FATAL':
        return app_name + ' | FATAL | ' + str(exc) + ' | unknown'
    elif severity == 'ANR':
        return app_name + ' | ANR | ' + str(tag) + ' | ' + str(msg)
    else:
        return app_name + ' | E:' + str(tag) + ' | ' + str(exc) + ' | unknown'

def generate_logcat_file(json_data, output_path, app_name):
    events = json_data.get('events', [])
    faults = [e for e in events if e.get('type') == 'fault']
    screens = [e for e in events if e.get('type') == 'screen']
    with open(output_path, 'w') as f:
        f.write('# Logcat for ' + app_name + '\n# Faults: ' + str(len(faults)) + '\n# Screens: ' + str(len(screens)) + '\n#' + '='*60 + '\n\n')
        for screen in screens:
            ts = screen.get('timestamp', 0)
            sn = screen.get('data', {}).get('screenName', 'Unknown')
            f.write('[' + str(ts).zfill(6) + '] I/ActivityManager: Displayed ' + str(sn) + '\n')
        f.write('\n')
        for fault in faults:
            ts = fault.get('timestamp', 0)
            data = fault.get('data', {})
            severity = data.get('severity', 'E')
            exc = data.get('exception', 'Unknown')
            msg = data.get('message', '')
            tag = data.get('tag', 'AndroidRuntime')
            log_level = 'F' if severity == 'FATAL' else 'W' if severity == 'ANR' else 'E'
            fault_key = generate_fault_key(fault, app_name)
            f.write('[' + str(ts).zfill(6) + '] ' + log_level + '/' + str(tag) + ': ' + str(exc) + ': ' + str(msg) + '\n')
            f.write('  # KEY: ' + fault_key + '\n\n')

def generate_placeholder_files(output_dir, tag):
    for i in range(1, 4):
        (output_dir / (tag + '_placeholder_' + str(i) + '.txt')).write_text('')

@click.command()
@click.option('--json-input', '-j', required=True, type=click.Path(exists=True))
@click.option('--output-dir', '-o', required=True, type=click.Path())
@click.option('--tag', '-t', required=True)
@click.option('--package', '-p', required=True)
@click.option('--fault-dir', '-f', type=click.Path())
def main(json_input, output_dir, tag, package, fault_dir):
    json_path = Path(json_input)
    output_base = Path(output_dir)
    coverage_dir = output_base / package / tag
    fault_dir = Path(fault_dir) / tag if fault_dir else output_base / 'logs' / tag
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    sate_coverage = convert_to_sate_coverage(json_data)
    coverage_dir.mkdir(parents=True, exist_ok=True)
    with open(coverage_dir / (tag + '_Jacoco.npy'), 'wb') as f:
        np.save(f, sate_coverage, allow_pickle=True)
    generate_placeholder_files(coverage_dir, tag)
    fault_dir.mkdir(parents=True, exist_ok=True)
    generate_logcat_file(json_data, fault_dir / (tag + '_bug.logcat'), package)

if __name__ == '__main__':
    main()
