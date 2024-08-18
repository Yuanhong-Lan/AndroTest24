# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
from evaluation.result_analyzer.analysis.correlation_analysis import Correlation

if __name__ == '__main__':
    Correlation.get_correlation_between_coverage_and_bug("3.0h", "3.0h")