# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
from evaluation.result_analyzer.study_analyzer import convergence_analysis
from evaluation.result_analyzer.study_analyzer.study_util import Experiments
from evaluation.result_analyzer.utils.data_util import DataType
from runtime_collection.unified_testing_config import empirical_app_list_all


if __name__ == '__main__':
    # convergence_analysis.present_and_export_coverage_convergence_result(
    #     target_app_dict=Experiments.EXPERIMENTAL_APP_DICT,
    #     testing_time=10800,
    #     postfix="@10",
    # )

    # convergence_analysis.FaultConvergenceTime.generate_raw_pickle_data(
    #     pattern_dict=Experiments.TAG_PATTERN_DICT,
    #     postfix="3.0h",
    #     target_time=10800,
    # )
    convergence_analysis.present_fault_convergence_result(postfix="3.0h", target_apps=empirical_app_list_all[:5])

    Experiments.get_correlation_between_times(DataType.Coverage)
    Experiments.get_correlation_between_times(DataType.Bug)
