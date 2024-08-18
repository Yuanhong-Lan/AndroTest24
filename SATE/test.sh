root_path=$(dirname $(readlink -f "$0"))
echo "Root path: $root_path"

analyzer_path=$root_path/evaluation/result_analyzer/study_analyzer
echo "Analyzer path: $analyzer_path"

export PYTHONPATH=$PYTHONPATH:$root_path
echo "Python path: $PYTHONPATH"

echo "Running the study analyzers"

echo "First, run the granularities analyzer..."
python $analyzer_path/granularities_analyzer.py
echo "Done."

echo "Second, run the metrics relation analyzer..."
python $analyzer_path/metrics_relation_analyzer.py
echo "Done."

echo "Third, run the randomness analyzer..."
python $analyzer_path/randomness_analyzer.py
echo "Done."

echo "Fourth, run the convergence analyzer..."
python $analyzer_path/convergence_analyzer.py
echo "Done."
