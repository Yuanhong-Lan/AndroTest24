# ----------------------
# @Time  : 2023 Mar
# @Author: Yuanhong Lan
# ----------------------
from enum import Enum
from typing import Tuple, Optional, Dict

import numpy as np
import scipy.stats
from numpy import ndarray
from pandas import DataFrame
from scipy import stats


class DataType(Enum):
    Coverage = "coverage"
    Bug = "bug"


class StatisticDataUtil:
    @staticmethod
    def get_coefficient_of_variation(all_data: ndarray) -> float:
        std = all_data.std(ddof=1)
        mean = all_data.mean()
        if std == 0:
            return 0
        return round(std / mean * 100, 2)

    @staticmethod
    def get_average_with_std_str(data: ndarray) -> str:
        return f"{data.mean():.2f}±{data.std(ddof=1):.2f}"

    @staticmethod
    def get_t_test_res(data1: ndarray, data2: ndarray) -> Tuple[str, str]:
        res: scipy.stats.stats.Ttest_indResult = stats.ttest_ind(data1, data2)
        t_statistic = res.statistic
        p_value = res.pvalue
        if np.isinf(t_statistic):
            t_statistic = np.nan
            p_value = np.nan
        return str(round(t_statistic, 3)), str(round(p_value, 3))

    @staticmethod
    def full_data_to_tool_ndarrays(full_data: DataFrame, tool_name: str, slicing: Optional[int] = None) -> Dict[str, ndarray]:
        res = {}

        tool_data = full_data.loc[tool_name, :]
        for column in tool_data.columns:
            res[column] = tool_data[column].to_numpy()
            if slicing is not None:
                res[column] = res[column][:slicing]

        return res
