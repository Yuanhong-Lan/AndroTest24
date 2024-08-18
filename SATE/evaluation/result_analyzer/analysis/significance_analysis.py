# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import itertools
import math
import os
import shutil
from typing import Dict, Optional, List

import numpy as np
import pandas as pd
from pandas import CategoricalDtype

from android_testing_utils.log import my_logger
from evaluation.result_analyzer.utils.data_util import DataType, StatisticDataUtil
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator
from runtime_collection import unified_testing_config


class Significance:
    SIGNIFICANCE_IDENTIFIER = "SIG"
    IS_SIGNIFICANT_IDENTIFIER = "isSIG"
    TOTAL_COUNT_IDENTIFIER = "TOTAL"

    @staticmethod
    def __generate_is_significant_column(
            data: pd.DataFrame,
            appointed_column: str,
            identifier: str,
    ) -> pd.DataFrame:
        data = pd.concat([data, pd.DataFrame(columns=[
            identifier,
        ], dtype=str)])
        for index, row in data.iterrows():
            t_value = row[appointed_column]
            if pd.isna(t_value):
                data.loc[index, identifier] = ""
                my_logger.hint(my_logger.LogLevel.WARNING, "Significance", False, f"Wrong with line: {index}  {row.tolist()}")
                continue

            symbol = row[appointed_column][0]
            if (symbol == "+" or symbol == "-") and (float(row[appointed_column][1:]) < 0.05):
                data.loc[index, identifier] = f"{symbol}{symbol}"
            else:
                data.loc[index, identifier] = ""
        return data

    @staticmethod
    def __generate_significance_column_from_raw_statistic_data(data: pd.DataFrame, identifier: str) -> pd.DataFrame:
        data = pd.concat([data, pd.DataFrame(columns=[
            identifier,
        ], dtype=str)])
        for index, row in data.iterrows():
            tool1_avg = float(row["TOOL1"].split("±")[0])
            tool2_avg = float(row["TOOL2"].split("±")[0])

            if tool1_avg == tool2_avg:
                data.loc[index, identifier] = "="
            elif pd.isna(row["T"]):
                if tool1_avg > tool2_avg:
                    data.loc[index, identifier] = "+ 0.00"
                elif tool1_avg < tool2_avg:
                    data.loc[index, identifier] = "- 0.00"
            elif row["T"] == 0:
                if tool1_avg > tool2_avg:
                    data.loc[index, identifier] = "+ 1.00"
                elif tool1_avg < tool2_avg:
                    data.loc[index, identifier] = "- 1.00"
            else:
                p_temp = str(row["P"])[:4]
                if tool1_avg > tool2_avg:
                    data.loc[index, identifier] = f"+ {p_temp}"
                else:
                    data.loc[index, identifier] = f"- {p_temp}"
        return data

    @staticmethod
    def __significance_analysis(file_to_read, file_to_write):
        data = pd.read_excel(file_to_read, index_col=0)

        data = Significance.__generate_significance_column_from_raw_statistic_data(data, Significance.SIGNIFICANCE_IDENTIFIER)
        data = Significance.__generate_is_significant_column(data, Significance.SIGNIFICANCE_IDENTIFIER, Significance.IS_SIGNIFICANT_IDENTIFIER)

        data.to_excel(file_to_write)

    @staticmethod
    def __split_raw_data_with_sig_to_sheets_by_types(file_to_read: str, file_to_write: str):
        data = pd.read_excel(file_to_read, index_col=0)

        res: Dict[str, pd.DataFrame] = {}
        for index, row in data.iterrows():
            app_name, domain = str(index).split("-")
            if domain not in res:
                res[domain] = pd.DataFrame(columns=data.columns)
            res[domain].loc[app_name] = row

        excel_writer = pd.ExcelWriter(file_to_write)
        for key, value in res.items():
            value.to_excel(excel_writer, sheet_name=key)
        excel_writer.save()

    @staticmethod
    def __combine_sig_data_and_get_counts(file_to_read: str, file_to_write: str, index_filter: Optional[List] = None):
        data = pd.read_excel(file_to_read, sheet_name=None, index_col=0, dtype=str)

        domain_count = len(data)
        domain_significant_count = math.ceil(domain_count * 2 / 3)

        if index_filter is not None:
            for domain, sheet in data.items():
                sheet.drop(list(set(sheet.index) - set(index_filter)), inplace=True)

        app_sorted_order = CategoricalDtype(unified_testing_config.SORTED_APP_NAME_LIST_BY_ACTIVITY, ordered=True)

        res1 = pd.DataFrame(columns=data.keys())
        res2 = pd.DataFrame(columns=data.keys())

        # get significance value and significance signs
        for domain, sheet in data.items():
            res1[domain] = sheet[Significance.SIGNIFICANCE_IDENTIFIER]
            res2[domain] = sheet[Significance.IS_SIGNIFICANT_IDENTIFIER]

        # sort by the appointed order
        res1.index = res1.index.astype(app_sorted_order)
        res1.sort_index(axis=0, inplace=True)
        res2.index = res2.index.astype(app_sorted_order)
        res2.sort_index(axis=0, inplace=True)

        excel_writer = pd.ExcelWriter(file_to_write)

        res1.to_excel(excel_writer, sheet_name=Significance.SIGNIFICANCE_IDENTIFIER)

        # count signs via columns
        count_column = pd.DataFrame()
        for column_name, column_data in res2.iteritems():
            count_column = pd.concat([count_column, pd.DataFrame(res2[column_name].value_counts())], axis=1)
        if "++" not in count_column.index:
            count_column.loc["++"] = np.nan
        if "--" not in count_column.index:
            count_column.loc["--"] = np.nan
        count_column = count_column.fillna(0)
        count_column.sort_index(axis=0, inplace=True)

        # count signs via lines
        count_line = pd.DataFrame()
        for index, row in res2.iterrows():
            count_line = pd.concat([count_line, pd.DataFrame(res2.loc[index].value_counts()).T], axis=0)
        if "++" not in count_line.columns:
            count_line["++"] = np.nan
        if "--" not in count_line.columns:
            count_line["--"] = np.nan
        count_line = count_line.fillna(0)
        count_line.sort_index(axis=1, inplace=True)

        # add extra analysis
        for index, row in count_line.iterrows():
            pos_cnt = row["++"]
            neg_cnt = row["--"]

            if pos_cnt >= domain_significant_count:
                count_line.loc[index, "R"] = '>>'
            elif neg_cnt >= domain_significant_count:
                count_line.loc[index, "R"] = '<<'
            else:
                count_line.loc[index, "R"] = np.nan

            if pos_cnt == domain_count or neg_cnt == domain_count:
                count_line.loc[index, "Same"] = '√'
            else:
                count_line.loc[index, "Same"] = np.nan

            for domain in res2.columns:
                if (not pd.isna(count_line.loc[index, "R"])) and (pd.isna(res2.loc[index, domain])):
                    count_line.loc[index, f"NotSig-{domain}"] = '√'
                else:
                    count_line.loc[index, f"NotSig-{domain}"] = np.nan

            for domain in res2.columns:
                if not pd.isna(count_line.loc[index, "R"]):
                    if count_line.loc[index, "R"] == ">>":
                        target = "--"
                    else:
                        target = "++"
                    if res2.loc[index, domain] == target:
                        count_line.loc[index, f"Conflict-{domain}"] = '√'
                    else:
                        count_line.loc[index, f"Conflict-{domain}"] = np.nan

        # add these counted data
        res2 = pd.concat([res2, count_line], axis=1)
        total = res2.count(axis=0)
        res2 = pd.concat([res2, count_column], axis=0)
        res2.loc[Significance.TOTAL_COUNT_IDENTIFIER] = total

        res2.to_excel(excel_writer, sheet_name=Significance.IS_SIGNIFICANT_IDENTIFIER)

        excel_writer.save()

        return total

    @staticmethod
    def original_data_to_raw_significance_data(
            original_data_path: str,
            tools: List[str],
            data_type: DataType,
            postfix: Optional[str] = None,
    ):
        original_data = pd.read_excel(original_data_path, index_col=0, header=0)
        tool_data_dict: Dict[str, Dict[str, np.ndarray]] = {
            tool : StatisticDataUtil.full_data_to_tool_ndarrays(original_data, tool)
            for tool in tools
        }
        for pair in itertools.combinations(tools, 2):
            tool1, tool2 = pair
            current_statistic_data = pd.DataFrame(
                columns=[tool1, tool2, "t", "p"],
                index=original_data.columns,
            )
            for column in original_data.columns:
                current_statistic_data.loc[column, tool1] = StatisticDataUtil.get_average_with_std_str(tool_data_dict[tool1][column])
                current_statistic_data.loc[column, tool2] = StatisticDataUtil.get_average_with_std_str(tool_data_dict[tool2][column])
                t, p = StatisticDataUtil.get_t_test_res(tool_data_dict[tool1][column], tool_data_dict[tool2][column])
                current_statistic_data.loc[column, "t"] = t
                current_statistic_data.loc[column, "p"] = p

            current_statistic_data = current_statistic_data[(~current_statistic_data[tool1].str.startswith('-'))&(~current_statistic_data[tool2].str.startswith('-'))]
            current_statistic_data.to_excel(os.path.join(
                ExcelDirectoryPathGenerator.get_raw_statistic_data_dir(data_type),
                f"{'-'.join(pair)}{'' if postfix is None else '_'+postfix}.xlsx"
            ))

    @staticmethod
    def full_significance_process_for_spssau_raw_data(
            raw_data_file_name: str,
            data_type: DataType,
            combine_to_one_target: pd.ExcelWriter = None,
            index_filter: Optional[List] = None,
    ):
        excel1 = os.path.join(ExcelDirectoryPathGenerator.get_temp_dir(data_type), f"{data_type.value}_t1_unified_raw_statistics.xlsx")
        excel2 = os.path.join(ExcelDirectoryPathGenerator.get_temp_dir(data_type), f"{data_type.value}_t2_statistics_with_sig.xlsx")
        excel3 = os.path.join(ExcelDirectoryPathGenerator.get_temp_dir(data_type), f"{data_type.value}_t3_statistics_with_sig_by_types.xlsx")
        excel4 = os.path.join(ExcelDirectoryPathGenerator.get_temp_dir(data_type), f"{data_type.value}_t4_coverage_sig.xlsx")

        raw_data = pd.read_excel(
            os.path.join(ExcelDirectoryPathGenerator.get_raw_statistic_data_dir(data_type), raw_data_file_name),
            index_col=0, header=None, dtype=str,skiprows=1,
        )
        raw_data.columns = ["TOOL1", "TOOL2", "T", "P"]
        raw_data.to_excel(excel1)

        Significance.__significance_analysis(file_to_read=excel1, file_to_write=excel2)
        Significance.__split_raw_data_with_sig_to_sheets_by_types(file_to_read=excel2, file_to_write=excel3)
        total_data = Significance.__combine_sig_data_and_get_counts(file_to_read=excel3, file_to_write=excel4, index_filter=index_filter)

        if combine_to_one_target is None:
            shutil.copy(excel4, os.path.join(ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type), raw_data_file_name))
        else:
            temp = pd.read_excel(excel4, index_col=0, dtype=str, sheet_name=None)
            for sheet_name, sheet_data in temp.items():
                sheet_data.to_excel(combine_to_one_target, sheet_name=f"{raw_data_file_name.split('.xlsx')[0]}_{sheet_name}")

        return total_data

    @staticmethod
    def full_significance_process_for_spssau_raw_data_all_tool_pairs(
            file_name_to_write: str,
            tools: List[str],
            data_type: DataType,
            index_filter: Optional[List] = None,
            postfix: Optional[str] = None,
    ):
        res_file = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type),
            f"{file_name_to_write}{'' if postfix is None else '_'+postfix}.xlsx"
        ))
        total_sheet = None
        for pair in ['-'.join(item) for item in itertools.combinations(tools, 2)]:
            total_data = Significance.full_significance_process_for_spssau_raw_data(
                f"{pair}{'' if postfix is None else '_'+postfix}.xlsx",
                data_type=data_type,
                combine_to_one_target=res_file,
                index_filter=index_filter
            )
            if total_sheet is None:
                total_sheet = pd.DataFrame(columns=total_data.index)
            total_sheet.loc[f"{pair}({Significance.TOTAL_COUNT_IDENTIFIER})"] = total_data
        total_sheet.drop(columns=["++", "--"], inplace=True)
        total_sheet.loc["SUM"] = total_sheet.sum(axis=0)
        total_sheet.to_excel(res_file, sheet_name=Significance.TOTAL_COUNT_IDENTIFIER)
        res_file.save()
        res_file.close()
