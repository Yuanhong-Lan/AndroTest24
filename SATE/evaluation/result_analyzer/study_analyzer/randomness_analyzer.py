# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
from evaluation.result_analyzer.study_analyzer.study_util import Experiments
from evaluation.result_analyzer.utils.data_util import DataType


if __name__ == '__main__':
    Experiments.get_all_cv_data(DataType.Coverage)
    Experiments.get_all_cv_data(DataType.Bug)
