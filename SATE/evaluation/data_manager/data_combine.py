# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import itertools
import os
import shutil
import time
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple

from pandas.api.types import CategoricalDtype

from android_testing_utils.log import my_logger
from constant import PlatformConstant
from evaluation.result_analyzer.study_analyzer.convergence_analysis import PERCENTAGE_TARGETS
from evaluation.result_analyzer.utils.coverage_util import CoverageTimeUtil, CoverageDataUtil
from evaluation.result_analyzer.utils.data_util import DataType
from evaluation.result_analyzer.utils.pattern_util import PatternUtil
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator
from runtime_collection import unified_testing_config
from runtime_collection.collector_util.util_coverage import CoverageItem, CoverageDetail, CoverageDetailWithStd, \
    get_readable_final_coverage_info_string
from runtime_collection.unified_testing_config import SORTED_TOOL_NAME_LIST, \
    SORTED_APP_NAME_LIST_BY_INSTRUCTION
from evaluation.result_analyzer.analysis.significance_analysis import Significance


class CoverageCombine:
    @staticmethod
    def __combine_coverage_raw_data_lists(
            raw_data_lists: List[List[CoverageItem]],
            need_std: bool = False,
            recalculate_std: bool = True,
            recalculate_rate: bool = True,
            same_package: bool = True,
    ):
        """Raw data combination for data lists."""
        full_time_list = []
        for raw_data in raw_data_lists:
            full_time_list.extend([i.time for i in raw_data])
        full_time_list = sorted(list(set(full_time_list)))

        for i in range(len(raw_data_lists)):
            raw_data_lists[i] = CoverageTimeUtil.padding_data(raw_data_lists[i], full_time_list)

        combined_coverage_data = []
        for i in range(len(full_time_list)):
            covered_list: List[float] = []
            total_list: List[float] = []
            rate_list: List[float] = []

            if not recalculate_std:
                std_list: List[float] = []
                std_upper_list: List[float] = []
                std_lower_list: List[float] = []

            for raw_data in raw_data_lists:
                assert raw_data[i].time == full_time_list[i]
                covered_list.append(raw_data[i].detail.covered)
                total_list.append(raw_data[i].detail.total)
                rate_list.append(raw_data[i].detail.rate)
                if not recalculate_std:
                    std_list.append(raw_data[i].detail.std)
                    std_upper_list.append(raw_data[i].detail.std_upper)
                    std_lower_list.append(raw_data[i].detail.std_lower)

            covered_avg = round(float(np.mean(covered_list)), 2)
            total = round(float(np.mean(total_list)), 2)
            if recalculate_rate:
                rate_avg = round(covered_avg / total, 4)
            else:
                rate_avg = round(float(np.mean(rate_list)), 4)
            if same_package:
                assert (np.array(total_list) == total).all()

            if not need_std:
                detail = CoverageDetail(
                    covered=covered_avg,
                    total=total,
                    rate=rate_avg
                )
            else:
                if not recalculate_std:
                    std = round(float(np.mean(std_list)), 4)
                    std_lower = round(float(np.mean(std_lower_list)), 4)
                    std_upper = round(float(np.mean(std_upper_list)), 4)
                else:
                    std = round(np.std(np.array(covered_list) / total), 4)
                    std_lower = round(rate_avg - std, 4)
                    std_upper = round(rate_avg + std, 4)
                detail = CoverageDetailWithStd(
                    covered=covered_avg,
                    total=total,
                    rate=rate_avg,
                    std=std,
                    std_lower=std_lower,
                    std_upper=std_upper
                )

            combined_coverage_data.append(
                CoverageItem(
                    full_time_list[i],
                    detail
                )
            )

        return CoverageDataUtil.extend_coverage_data_list_with_standard_time_series(
            combined_coverage_data, PlatformConstant.TIME_LENGTH, PlatformConstant.TIME_INTERVAL, need_std
        )

    @staticmethod
    def __combine_coverage_raw_data_dicts(
            raw_data_dicts: List[Dict[str, List[CoverageItem]]],
            need_std: bool,
            recalculate_std: bool,
            recalculate_rate: bool,
            same_package: bool,
    ):
        """Raw data combination for data dicts (with different types)."""
        res: Dict[str, List[CoverageItem]] = {}
        for data_type in raw_data_dicts[0].keys():
            raw_data_list = [data[data_type] for data in raw_data_dicts]
            res[data_type] = CoverageCombine.__combine_coverage_raw_data_lists(
                raw_data_lists=raw_data_list,
                need_std=need_std,
                recalculate_std=recalculate_std,
                recalculate_rate=recalculate_rate,
                same_package=same_package,
            )
        return res

    @staticmethod
    def __combine_packages_with_tag_pattern(
            tag_pattern: str,
            need_std: bool = False,
            target_apps: Optional[List[unified_testing_config.Apps]] = None,
    ):
        for package in os.listdir(PlatformConstant.COVERAGE_DATA_ROOT_DIR):
            if (target_apps is not None) and (unified_testing_config.get_app_by_package_name(package) not in target_apps):
                continue
            package_dir = os.path.join(PlatformConstant.COVERAGE_DATA_ROOT_DIR, package)

            data_to_combine: List[Dict[str, List[CoverageItem]]] = []
            tag_to_combine = []
            for tag in os.listdir(package_dir):
                if PatternUtil.is_match(tag_pattern, tag):
                    tag_to_combine.append(tag)
                    tag_dir = os.path.join(package_dir, tag)

                    temp = {}
                    if len(os.listdir(tag_dir)) != 4:
                        my_logger.hint(my_logger.LogLevel.WARNING, "DataUtil", False, f"Not 4 items, Continue! {tag_dir}")
                        continue
                    for file in os.listdir(tag_dir):
                        if file.endswith(".npy"):
                            data: Dict[str, List[CoverageItem]] = np.load(os.path.join(tag_dir, file), allow_pickle=True).item()
                            temp.update(data)
                    data_to_combine.append(temp)

            if len(tag_to_combine) == 0:
                my_logger.hint(my_logger.LogLevel.WARNING, "DataUtil", False, f"Nothing to combine for {package}")
                continue

            combine_tag = tag_pattern.replace('**', '') if '**' in tag_pattern else tag_pattern[:-1]
            save_dir = os.path.join(package_dir, f"{combine_tag}@{len(data_to_combine)}")
            if os.path.exists(save_dir):
                s = input(f"Path {save_dir} exists, remove?(y/n)")
                if s == 'y':
                    shutil.rmtree(save_dir)
                else:
                    print("Don't remove, continue!")
                    continue

            os.makedirs(save_dir)

            file_name_prefix = f"{package}_Coverage_{time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())}"
            raw_file_path = os.path.join(save_dir, f"{file_name_prefix}.npy")
            log_file_path = os.path.join(save_dir, f"{file_name_prefix}.txt")

            res = CoverageCombine.__combine_coverage_raw_data_dicts(
                raw_data_dicts=data_to_combine,
                need_std=need_std,
                recalculate_std=True,
                recalculate_rate=True,
                same_package=True,
            )

            np.save(raw_file_path, res)

            res_string = get_readable_final_coverage_info_string(res)
            with open(log_file_path, 'w') as f:
                f.write(res_string)
                my_logger.hint(my_logger.LogLevel.INFO, "DataUtil", False,
                               f"Combined Coverage Result save to {log_file_path}")
            my_logger.hint(my_logger.LogLevel.INFO, "DataUtil", False, f"{package}  {tag_to_combine}:{len(tag_to_combine)}")

    @staticmethod
    def __combine_to_one_with_tag_list(
            tag_list: List[str],
            combined_tag: str,
            need_std: bool,
    ):

        expected_file_num = 2 if '@' in tag_list[0] else 4

        data_to_combine: List[Dict[str, List[CoverageItem]]] = []
        target_to_combine: List[Tuple[str, str]] = []

        for package in os.listdir(PlatformConstant.COVERAGE_DATA_ROOT_DIR):
            package_dir = os.path.join(PlatformConstant.COVERAGE_DATA_ROOT_DIR, package)

            for tag in os.listdir(package_dir):
                if tag in tag_list:
                    tag_dir = os.path.join(package_dir, tag)
                    temp = {}
                    if len(os.listdir(tag_dir)) != expected_file_num:
                        my_logger.hint(my_logger.LogLevel.WARNING, "DataUtil", False, f"Not {expected_file_num} items, Continue! {tag_dir}")
                        continue
                    for file in os.listdir(tag_dir):
                        if file.endswith(".npy"):
                            data: Dict[str, List[CoverageItem]] = np.load(os.path.join(tag_dir, file), allow_pickle=True).item()
                            temp.update(data)

                    target_to_combine.append((package, tag))
                    temp = CoverageTimeUtil.normalize_time_for_data_dict(temp, PlatformConstant.TIME_LENGTH)
                    temp = CoverageDataUtil.extend_coverage_data_dict_with_standard_time_series(temp, PlatformConstant.TIME_LENGTH, PlatformConstant.TIME_INTERVAL, need_std)
                    temp = CoverageDataUtil.filter_coverage_data_dict_with_standard_time_series(temp, PlatformConstant.TIME_LENGTH, PlatformConstant.TIME_INTERVAL)
                    data_to_combine.append(temp)

        if len(target_to_combine) == 0:
            my_logger.hint(my_logger.LogLevel.WARNING, "DataUtil", False, f"Nothing to combine for {tag_list}, exit!")
            return
        else:
            print(f"The following [{len(data_to_combine)}] targets will be combined!")
            for target in target_to_combine:
                print(f"\t{target}")
            s = input("Continue?(y/n)")
            if s != 'y':
                print("Exit!")
                return

        save_dir = os.path.join(PlatformConstant.STATISTICS_DATA_ROOT_DIR, f"{combined_tag}@{len(data_to_combine)}")
        if os.path.exists(save_dir):
            s = input(f"Path {save_dir} exists, remove?(y/n)")
            if s == 'y':
                shutil.rmtree(save_dir)
            else:
                print("Don't remove, exit!")
                return

        os.makedirs(save_dir)

        file_name_prefix = f"{combined_tag}_Coverage_{time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())}"
        raw_file_path = os.path.join(save_dir, f"{file_name_prefix}.npy")
        log_file_path = os.path.join(save_dir, f"{file_name_prefix}.txt")

        res = CoverageCombine.__combine_coverage_raw_data_dicts(
            raw_data_dicts=data_to_combine,
            need_std=need_std,
            recalculate_std=False,
            recalculate_rate=False,
            same_package=False,
        )

        np.save(raw_file_path, res)

        res_string = get_readable_final_coverage_info_string(res)
        with open(log_file_path, 'w') as f:
            f.write(res_string)
            my_logger.hint(my_logger.LogLevel.INFO, "DataUtil", False,
                           f"Combined Coverage Result save to {log_file_path}")

    @staticmethod
    def combine_packages_with_pattern(pattern, need_std=True, target_apps: Optional[List[unified_testing_config.Apps]] = None):
        """CoverageCombine data with the same prefix by packages, e.g., ARES-0622-uni~"""
        CoverageCombine.__combine_packages_with_tag_pattern(tag_pattern=pattern, need_std=need_std, target_apps=target_apps)

    @staticmethod
    def combine_to_one_with_prefix(prefix, combined_tag):
        """CoverageCombine data with the listed tags across packages, e.g., ARES-0622-uni@5"""
        CoverageCombine.__combine_to_one_with_tag_list(
            tag_list=[f"{prefix}@5"],
            combined_tag=combined_tag,
            need_std=True,
        )


def from_full_data_to_average_data(file_to_read: str, file_to_write: str, data_type: DataType):
    file_path_to_read = os.path.join(ExcelDirectoryPathGenerator.get_original_data_dir(data_type), file_to_read)
    file_path_to_write = os.path.join(ExcelDirectoryPathGenerator.get_original_data_dir(data_type), file_to_write)

    df = pd.read_excel(file_path_to_read, index_col=0)  # Assuming the first column is the index

    df_grouped = df.groupby(df.index).mean()

    if data_type == DataType.Coverage:
        df_grouped = df_grouped.round(2)

    res = {}
    for column in df_grouped.columns:
        app_name, sub_metric = column.split('-')
        if sub_metric not in res:
            res[sub_metric] = pd.DataFrame(index=df_grouped.index)
        res[sub_metric][app_name] = df_grouped[column]

    excel_writer = pd.ExcelWriter(file_path_to_write)
    for sub_metric, df_sub in res.items():
        df_sub = df_sub.transpose()

        my_index_order = CategoricalDtype(SORTED_APP_NAME_LIST_BY_INSTRUCTION, ordered=True)
        df_sub.index = df_sub.index.astype(my_index_order)
        df_sub.sort_index(axis=0, inplace=True)

        my_columns_order = CategoricalDtype(SORTED_TOOL_NAME_LIST, ordered=True)
        df_sub.columns = df_sub.columns.astype(my_columns_order)
        df_sub.sort_index(axis=1, inplace=True)

        df_sub.to_excel(excel_writer, sheet_name=sub_metric)

    excel_writer.save()


def from_average_data_to_average_cmp_data(file_to_read: str, file_to_write: str, data_type: DataType):
    file_path_to_read = os.path.join(ExcelDirectoryPathGenerator.get_original_data_dir(data_type), file_to_read)
    file_path_to_write = os.path.join(ExcelDirectoryPathGenerator.get_original_data_dir(data_type), file_to_write)

    dfs = pd.read_excel(file_path_to_read, index_col=0, sheet_name=None)

    tool_pairs = ['-'.join(item) for item in itertools.combinations(SORTED_TOOL_NAME_LIST, 2)]
    res = {}
    for sheet_name, sheet_data in dfs.items():
        res[sheet_name] = pd.DataFrame(index=SORTED_APP_NAME_LIST_BY_INSTRUCTION, columns=tool_pairs, dtype=int)
        for app in SORTED_APP_NAME_LIST_BY_INSTRUCTION:
            n = len(SORTED_TOOL_NAME_LIST)
            for i in range(n):
                for j in range(i + 1, n):
                    tool1 = SORTED_TOOL_NAME_LIST[i]
                    tool2 = SORTED_TOOL_NAME_LIST[j]
                    if sheet_data.loc[app, tool1] == -1 or sheet_data.loc[app, tool2] == -1:
                        res[sheet_name].loc[app, f"{tool1}-{tool2}"] = np.nan
                    elif sheet_data.loc[app, tool1] > sheet_data.loc[app, tool2]:
                        res[sheet_name].loc[app, f"{tool1}-{tool2}"] = 1
                    elif sheet_data.loc[app, tool1] < sheet_data.loc[app, tool2]:
                        res[sheet_name].loc[app, f"{tool1}-{tool2}"] = -1
                    else:
                        res[sheet_name].loc[app, f"{tool1}-{tool2}"] = 0

    app_pairs = [f"{app}_{pair}" for app in SORTED_APP_NAME_LIST_BY_INSTRUCTION for pair in tool_pairs]
    df_all = pd.DataFrame(index=app_pairs, columns=dfs.keys(), dtype=int)
    for sub_metric, df_sub in res.items():
        for app in SORTED_APP_NAME_LIST_BY_INSTRUCTION:
            for pair in tool_pairs:
                if not np.isnan(df_sub.loc[app, pair]):
                    df_all.loc[f"{app}_{pair}", sub_metric] = df_sub.loc[app, pair]
    df_all.dropna(inplace=True)
    df_all_corr = df_all.corr()
    res["all_data"] = df_all
    res["all_data_corr"] = df_all_corr

    temp = df_all.iloc[:, :-1]
    all_equal = temp.apply(lambda row: (row == row.iloc[0]).all(), axis=1)
    print(all_equal.sum(), len(all_equal), all_equal.sum() / len(all_equal))
    df_all["equal_3"] = all_equal

    excel_writer = pd.ExcelWriter(file_path_to_write)
    for sub_metric, df_sub in res.items():
        df_sub.to_excel(excel_writer, sheet_name=sub_metric)

    excel_writer.save()


def from_significance_data_to_tool_significance_level(file_to_read: str, file_to_write: str, data_type: DataType):
    file_path_to_read = os.path.join(ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type), file_to_read)
    file_path_to_write = os.path.join(ExcelDirectoryPathGenerator.get_processed_statistic_data_dir(data_type), file_to_write)

    dfs = pd.read_excel(file_path_to_read, index_col=0, sheet_name=None)  # Assuming the first column is the index
    res = {}

    for sheet_name, sheet_data in dfs.items():
        if not sheet_name.endswith(Significance.IS_SIGNIFICANT_IDENTIFIER):
            continue
        tool1, tool2 = sheet_name.split('_')[0].split('-')
        target_columns = sheet_data.columns[:4]
        target_indexes = sheet_data.index[:42]
        for column in target_columns:
            if column not in res:
                res[column] = pd.DataFrame(index=SORTED_APP_NAME_LIST_BY_INSTRUCTION, columns=SORTED_TOOL_NAME_LIST, dtype=int)
                res[column].fillna(0, inplace=True)
            for index in target_indexes:
                if sheet_data.loc[index, column] == '++':
                    res[column].loc[index, tool1] += 1
                    res[column].loc[index, tool2] -= 1
                elif sheet_data.loc[index, column] == '--':
                    res[column].loc[index, tool2] += 1
                    res[column].loc[index, tool1] -= 1

    excel_writer = pd.ExcelWriter(file_path_to_write)
    for sub_metric, df_sub in res.items():
        df_sub.to_excel(excel_writer, sheet_name=sub_metric)

    excel_writer.save()


def combine_cv_data_to_one(file_to_write, tasks):
    res = {}

    def add_data(file_name, submetric_targets):
        cv_data_path = os.path.join(ExcelDirectoryPathGenerator.get_cv_data_dir(), file_name)
        dfs = pd.read_excel(cv_data_path, index_col=0, sheet_name=None)
        for sheet_name, sheet_data in dfs.items():
            tool = sheet_name.split('|')[1]
            if 'cv' not in sheet_name or tool not in SORTED_TOOL_NAME_LIST:
                continue
            for column in sheet_data.columns:
                if column not in submetric_targets:
                    continue
                if column not in res:
                    res[column] = pd.DataFrame(index=list(range(3, 11)), columns=SORTED_TOOL_NAME_LIST)
                res[column][tool] = sheet_data[column]

    for file_name, targets in tasks.items():
        add_data(file_name, targets)

    excel_writer = pd.ExcelWriter(os.path.join(ExcelDirectoryPathGenerator.get_cv_data_dir(), file_to_write))
    for sub_metric, df_sub in res.items():
        df_sub.to_excel(excel_writer, sheet_name=sub_metric)

    excel_writer.save()


tool_mapping = {item.lower(): item for item in SORTED_TOOL_NAME_LIST}
def combine_convergence_data_to_one(file_to_write, tasks, get_average=False):
    res = {}

    def add_data(file_name, data_type, submetric_mapping):
        convergence_data_path = os.path.join(ExcelDirectoryPathGenerator.get_time_data_dir(data_type), file_name)
        dfs = pd.read_excel(convergence_data_path, index_col=0, sheet_name=None)
        for sheet_name, sheet_data in dfs.items():
            raw_tool = sheet_name.split('~')[0].split('-')[-1]
            tool = tool_mapping[raw_tool]
            for column in sheet_data.columns:
                if not column.endswith('%'):
                    continue
                submetric_identifier, percentage = column.split('-')
                submetric = submetric_mapping[submetric_identifier]
                if submetric not in res:
                    res[submetric] = pd.DataFrame(index=PERCENTAGE_TARGETS, columns=SORTED_TOOL_NAME_LIST)
                res[submetric].loc[int(percentage[:-1]), tool] = sheet_data.loc["avg-all", column]

    for file_name, targets in tasks.items():
        add_data(file_name, *targets)

    # Path to save the temporary Excel file
    temp_file_path = os.path.join(ExcelDirectoryPathGenerator.get_time_data_dir(None), file_to_write)
    excel_writer = pd.ExcelWriter(temp_file_path, engine='openpyxl')
    for sub_metric, df_sub in res.items():
        if get_average:
            df_sub["avg-all"] = np.round(df_sub.mean(axis=1), 2)
        df_sub.to_excel(excel_writer, sheet_name=sub_metric)

    excel_writer.save()


# if __name__ == '__main__':
#     from evaluation.result_analyzer.study_analyzer.study_util import Experiments
#     for current_pattern, current_target_apps in Experiments.EXPERIMENTAL_APP_DICT.items():
#         CoverageCombine.combine_packages_with_pattern(
#             pattern=current_pattern,
#             need_std=True,
#             target_apps=current_target_apps,
#         )
#
#     CoverageCombine.combine_to_one_with_prefix("DQT-1125-uni", "DQT0807")
#
#     from_full_data_to_average_data(
#         "coverage_full_data_3.0h.xlsx",
#         "coverage_average_data_3.0h.xlsx",
#         DataType.Coverage,
#     )
#     from_average_data_to_average_cmp_data(
#         "coverage_average_data_3.0h.xlsx",
#         "coverage_average_cmp_data_3.0h.xlsx",
#         DataType.Coverage,
#     )
#     from_full_data_to_average_data(
#         "bug_full_data_3.0h.xlsx",
#         "bug_average_data_3.0h.xlsx",
#         DataType.Bug,
#     )
#
#     from_significance_data_to_tool_significance_level(
#         "coverage_ALL_TOOL_PAIRS_3.0h.xlsx",
#         "coverage_tool_significance_level_3.0h.xlsx",
#         DataType.Coverage,
#     )
#     from_significance_data_to_tool_significance_level(
#         "bug_ALL_TOOL_PAIRS_3.0h.xlsx",
#         "bug_tool_significance_level_3.0h.xlsx",
#         DataType.Bug,
#     )
#     combine_cv_data_to_one(
#         "all_cv_data.xlsx",
#         {
#             "coverage_3.0h-all.xlsx": ["INSTRUCTION", "LINE", "METHOD", "ACTIVITY"],
#             "bug_3.0h-all.xlsx": ["F", "V", "E+", "E", "UF", "UV", "UE+", "UE"],
#         }
#     )
#     combine_cv_data_to_one(
#         "derived_cv_data.xlsx",
#         {
#             "bug_3.0h-all.xlsx": ["UF", "UV", "UE+", "UE", "T3F", "T3V", "T3E+", "T3E", "T5F", "T5V", "T5E+", "T5E"],
#         }
#     )
#     combine_convergence_data_to_one(
#         "all_convergence_data.xlsx",
#         {
#             "coverage_time_convergence_data.xlsx": [DataType.Coverage, {"I": "INST", "L": "LINE", "M": "METH", "A": "ACTV"}],
#             "fault_time_convergence_data.xlsx": [DataType.Bug, {"F": "Level F", "V": "Level V", "E+": "Level E+", "E": "Level E"}],
#         },
#         get_average=True,
#     )