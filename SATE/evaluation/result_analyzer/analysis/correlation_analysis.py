# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import os
from typing import List, Tuple

import numpy as np
import pandas as pd

from android_testing_utils.log import my_logger
from evaluation.result_analyzer.analysis.significance_analysis import Significance
from evaluation.result_analyzer.utils.data_util import DataType
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator


class Correlation:
    @staticmethod
    def sig_value_to_float(x):
        if pd.isna(x):
            return np.nan
        res = 0
        if x != "=":
            sign, value = x.split(" ")
            if sign == "+":
                res = 1 - float(value)
            elif sign == "-":
                res = - (1 - float(value))
            else:
                assert False
        return res

    @staticmethod
    def get_correlation_between_metrics(file_name_to_read: str, data_type: DataType):
        data = pd.read_excel(
            os.path.join(ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type), file_name_to_read),
            index_col=0, sheet_name=None, dtype=str
        )

        excel_writer = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type), file_name_to_read.replace(".xlsx", "_CORR.xlsx")
        ))

        all_data = pd.DataFrame()
        for sheet_name, sheet_data in data.items():
            if sheet_name.endswith(f"_{Significance.SIGNIFICANCE_IDENTIFIER}"):
                all_data = pd.concat([
                    all_data,
                    sheet_data.rename(index=lambda x: f"[{sheet_name.split('_')[0]}]{x}")
                ], axis=0)

        all_data_float = all_data.applymap(Correlation.sig_value_to_float)

        corr_res = all_data_float.corr()

        all_data.to_excel(excel_writer, sheet_name="raw_data")
        all_data_float.to_excel(excel_writer, sheet_name="float_data")
        corr_res.to_excel(excel_writer, sheet_name="corr_result")

        my_logger.hint(my_logger.LogLevel.INFO, "Significance", False, f"Correlation Result:\n{corr_res}")

        excel_writer.save()

    @staticmethod
    def get_correlation_between_time(postfix_pair_list: List[Tuple[str, str]], file_postfix, data_type: DataType):
        res = pd.DataFrame()

        for post_fix_1, post_fix_2 in postfix_pair_list:
            data1 = pd.read_excel(
                os.path.join(
                    ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type),
                    f"{data_type.value}_ALL_TOOL_PAIRS_{post_fix_1}_CORR.xlsx"
                ),
                index_col=0, sheet_name="float_data", dtype=str
            ).applymap(float)
            data2 = pd.read_excel(
                os.path.join(
                    ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type),
                    f"{data_type.value}_ALL_TOOL_PAIRS_{post_fix_2}_CORR.xlsx"
                ),
                index_col=0, sheet_name="float_data", dtype=str
            ).applymap(float)
            for column in data1.columns:
                res.loc[f"{post_fix_1}_{post_fix_2}", column] = round(data1[column].corr(data2[column]), 3)

        res.to_excel(os.path.join(ExcelDirectoryPathGenerator.get_correlation_data_dir(), f"{data_type.value}_time_CORR{file_postfix}.xlsx"))

    @classmethod
    def get_correlation_between_coverage_and_bug(cls, coverage_postfix, bug_postfix):
        coverage_data = pd.read_excel(
            os.path.join(
                ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(DataType.Coverage),
                f"{DataType.Coverage.value}_ALL_TOOL_PAIRS{'' if coverage_postfix is None else '_' + coverage_postfix}_CORR.xlsx"
            ),
            sheet_name="float_data", index_col=0,
        )
        bug_data = pd.read_excel(
            os.path.join(
                ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(DataType.Bug),
                f"{DataType.Bug.value}_ALL_TOOL_PAIRS{'' if bug_postfix is None else '_' + bug_postfix}_CORR.xlsx"
            ),
            sheet_name="float_data", index_col=0,
        )
        all_data = pd.concat([coverage_data, bug_data], axis=1)
        assert len(coverage_data) == len(bug_data) == len(all_data)

        res = pd.DataFrame()
        for coverage_domain in coverage_data.columns:
            for bug_domain in bug_data.columns:
                res.loc[coverage_domain, bug_domain] = all_data[coverage_domain].corr(all_data[bug_domain])
        res.to_excel(os.path.join(ExcelDirectoryPathGenerator.get_correlation_data_dir(), f"Coverage_Bug_CORR.xlsx"))
