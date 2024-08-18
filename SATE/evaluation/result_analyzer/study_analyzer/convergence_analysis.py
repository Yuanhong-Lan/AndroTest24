# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import math
import os
import pickle
from typing import NamedTuple, List, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from constant import PlatformConstant
from evaluation.result_analyzer.study_analyzer.study_util import Experiments
from evaluation.result_analyzer.utils.coverage_util import CoverageTimeUtil, CoverageDataUtil
from evaluation.result_analyzer.utils.data_util import DataType
from evaluation.result_analyzer.utils.fault_util import BugAnalyzer, AbstractItem, FaultDomain, LogcatUtil
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator
from evaluation.result_analyzer.utils.pattern_util import PatternUtil
from runtime_collection.collector_util.util_coverage import CoverageItem
from runtime_collection.unified_testing_config import Apps, get_app_by_package_name, get_app_name_by_package_name, \
    SORTED_APP_NAME_LIST_BY_INSTRUCTION, empirical_app_list_all_for_combodroid


class CoverageConvergenceTimeItem(NamedTuple):
    final_coverage: float
    percent_90_time: int
    percent_95_time: int
    percent_98_time: int
    percent_100_time: int
    end_time: int


PERCENTAGE_TARGETS = list(range(0, 80, 5)) + list(range(80, 95, 2)) + list(range(95, 101, 1))

class CoverageConvergenceTimeFlexibleItem(NamedTuple):
    final_coverage: float
    percent_n_time: Dict[int, int]
    end_time: int

class CoverageConvergenceTime:
    @staticmethod
    def analyze_coverage_convergence_time_for_data_list(
            coverage_data: List[CoverageItem],
    ) -> CoverageConvergenceTimeItem:
        final_coverage = coverage_data[-1].detail.rate
        end_time = coverage_data[-1].time
        percent_90_time = None
        percent_95_time = None
        percent_98_time = None
        percent_100_time = None

        for item in coverage_data:
            if percent_90_time is None:
                if item.detail.rate >= 0.9 * final_coverage:
                    percent_90_time = item.time
            if percent_95_time is None:
                if item.detail.rate >= 0.95 * final_coverage:
                    percent_95_time = item.time
            if percent_98_time is None:
                if item.detail.rate >= 0.98 * final_coverage:
                    percent_98_time = item.time
            if percent_100_time is None:
                if item.detail.rate >= final_coverage:
                    percent_100_time = item.time
                    break

        return CoverageConvergenceTimeItem(
            final_coverage=final_coverage,
            percent_90_time=percent_90_time,
            percent_95_time=percent_95_time,
            percent_98_time=percent_98_time,
            percent_100_time=percent_100_time,
            end_time=end_time,
        )

    @staticmethod
    def analyze_coverage_convergence_time_for_data_list_flexible(
            coverage_data: List[CoverageItem],
    ) -> CoverageConvergenceTimeFlexibleItem:
        final_coverage = coverage_data[-1].detail.rate
        end_time = coverage_data[-1].time
        targets = PERCENTAGE_TARGETS
        percent_n_time = {target:None for target in targets}

        for item in coverage_data:
            for target in targets:
                if percent_n_time[target] is None:
                    if item.detail.rate >= target / 100 * final_coverage:
                        percent_n_time[target] = item.time
        return CoverageConvergenceTimeFlexibleItem(
            final_coverage=final_coverage,
            percent_n_time=percent_n_time,
            end_time=end_time,
        )

    @staticmethod
    def analyze_coverage_convergence_time_for_data_dict(
            coverage_data_dict: Dict[str, List[CoverageItem]],
    ) -> Dict[str, CoverageConvergenceTimeItem]:
        res = {}
        for key, value in coverage_data_dict.items():
            res[key] = CoverageConvergenceTime.analyze_coverage_convergence_time_for_data_list(value)
        return res

    @staticmethod
    def analyze_coverage_convergence_time_for_data_dict_flexible(
            coverage_data_dict: Dict[str, List[CoverageItem]],
    ) -> Dict[str, CoverageConvergenceTimeFlexibleItem]:
        res = {}
        for key, value in coverage_data_dict.items():
            res[key] = CoverageConvergenceTime.analyze_coverage_convergence_time_for_data_list_flexible(value)
        return res

    @staticmethod
    def analyze_coverage_convergence_time_for_all_packages_with_tag_pattern(
            tag_pattern: str,
            target_apps: List[Apps],
            testing_time: int,
            postfix: str = None,
    ) -> pd.DataFrame:
        res = pd.DataFrame()

        for package in os.listdir(PlatformConstant.COVERAGE_DATA_ROOT_DIR):
            if get_app_by_package_name(package) not in target_apps:
                continue
            package_dir = os.path.join(PlatformConstant.COVERAGE_DATA_ROOT_DIR, package)
            for tag in os.listdir(package_dir):
                if ((postfix is not None) and tag.endswith(postfix)) and (PatternUtil.is_match(tag_pattern, tag)):
                    tag_dir = os.path.join(package_dir, tag)
                    for file in os.listdir(tag_dir):
                        if file.endswith(".npy"):
                            file_path = os.path.join(tag_dir, file)
                            data: Dict[str, List[CoverageItem]] = np.load(file_path, allow_pickle=True).item()
                            data = CoverageTimeUtil.normalize_time_for_data_dict(data, testing_time)
                            data = CoverageDataUtil.extend_coverage_data_dict_with_standard_time_series(data, testing_time, 10, False)
                            # current_result_dict = CoverageConvergenceTime.analyze_coverage_convergence_time_for_data_dict(data)
                            current_result_dict = CoverageConvergenceTime.analyze_coverage_convergence_time_for_data_dict_flexible(data)

                            res_index = f"{get_app_name_by_package_name(package)}"
                            res.loc[res_index, "tag"] = tag

                            target_keys = ["INSTRUCTION", "LINE", "METHOD", "ACTIVITY"]
                            for coverage_key in target_keys:
                                convergence_value = current_result_dict[coverage_key]
                                res_column_prefix = coverage_key[:1]
                                for target in convergence_value.percent_n_time.keys():
                                    res.loc[res_index, f"{res_column_prefix}-{target}%"] = str(convergence_value.percent_n_time[target])
                                # res.loc[res_index, f"{res_column_prefix}-90%"] = str(convergence_value.percent_90_time)
                                # res.loc[res_index, f"{res_column_prefix}-95%"] = str(convergence_value.percent_95_time)
                                # res.loc[res_index, f"{res_column_prefix}-98%"] = str(convergence_value.percent_98_time)
                                # res.loc[res_index, f"{res_column_prefix}-100%"] = str(convergence_value.percent_100_time)
                                res.loc[res_index, f"{res_column_prefix}-cov"] = convergence_value.final_coverage * 100
                            break

        for column in res.columns:
            if column.endswith("%"):
                res[column] = res[column].astype(int)

        from pandas.api.types import CategoricalDtype
        my_order = CategoricalDtype(categories=SORTED_APP_NAME_LIST_BY_INSTRUCTION, ordered=True)
        res.index = res.index.astype(my_order)
        res.sort_index(axis=0, inplace=True)
        return res


def add_statistical_data(data, target_data_type: type):
    for column in data.columns:
        if column.endswith("%"):
            data[column] = data[column].astype(target_data_type)

    statistics_data = pd.DataFrame(columns=data.columns, dtype=target_data_type)
    statistics_data.loc["avg-l"] = data.apply(lambda x: target_data_type(round(x[:(data.shape[0] // 2)].mean(), 2)) if x.dtype == target_data_type else "")
    statistics_data.loc["avg-s"] = data.apply(lambda x: target_data_type(round(x[(data.shape[0] // 2):].mean(), 2)) if x.dtype == target_data_type else "")
    statistics_data.loc["avg-all"] = data.apply(lambda x: target_data_type(round(x.mean(), 2)) if x.dtype == target_data_type else "")

    return pd.concat([data, statistics_data], axis=0)


def present_and_export_coverage_convergence_result(target_app_dict: Dict[str, List[Apps]], testing_time, postfix):
    result_dir_path = ExcelDirectoryPathGenerator.get_time_data_dir(DataType.Coverage)

    excel_writer = pd.ExcelWriter(os.path.join(result_dir_path, "coverage_time_convergence_data.xlsx"))

    for target, target_apps in target_app_dict.items():
        data = CoverageConvergenceTime.analyze_coverage_convergence_time_for_all_packages_with_tag_pattern(
            target, target_apps, testing_time, postfix,
        )
        data = add_statistical_data(data, target_data_type=int)

        data = data.apply(lambda x: x.apply(lambda y: "%.2f" % (y/3600)) if x.dtype == int else x)
        data.to_excel(excel_writer, sheet_name=f"{target}_{postfix}")

    excel_writer.save()


class FaultConvergenceTime:
    @classmethod
    def generate_raw_pickle_data(cls, pattern_dict, postfix, target_time):
        for pattern in pattern_dict.keys():
            abstract_dict, combined_result = BugAnalyzer.analyze(
                app_str=None,
                pattern=pattern,
                tag_list=None,
                detail_level=0,
                show_each=False,
                show_final=False,
                target_time=target_time,
                only_save_one_for_each_file_when_combining=True,
            )

            with open(os.path.join(
                    ExcelDirectoryPathGenerator.get_pickle_data_dir(DataType.Bug, postfix), f"{pattern}.pkl"
            ), 'wb') as f:
                pickle.dump(combined_result, f)

    @classmethod
    def read_pickled_abstract_dict(cls, data_type: DataType, raw_pattern, postfix: Optional[str] = None) -> Dict[str, List[AbstractItem]]:
        file_path = os.path.join(
            ExcelDirectoryPathGenerator.get_pickle_data_dir(data_type, postfix), f"{raw_pattern}.pkl"
        )
        with open(file_path, "rb") as f:
            return pickle.load(f)

    @classmethod
    def abstract_dict_to_min_list(
            cls,
            abstract_dict: Dict[str, List[AbstractItem]],
            app_name_filter: Optional[List[str]],
    ) -> List[Tuple[float, str]]:
        res = []
        for bug_key, bug_list in abstract_dict.items():
            if app_name_filter is not None:
                if bug_key.split('|')[0].strip() not in app_name_filter:
                    continue
            # current_time_list = [item.relative_time for item in bug_list]
            # res.append((min(current_time_list), bug_key))
            for item in bug_list:
                res.append((item.relative_time, bug_key))
        return res

    @classmethod
    def calculate_fault_discover_time(cls, item_name: str, min_list: List[Tuple[float, str]]):
        target_per_list = PERCENTAGE_TARGETS
        columns = []
        for fault_domain in list(FaultDomain):
            columns.append(f"{fault_domain.value}-n")
            columns += [f"{fault_domain.value}-{i}%" for i in target_per_list]
        res = pd.DataFrame(columns=columns)
        for column in res.columns:
            if column.endswith("%"):
                res[column] = res[column].astype(float)

        min_list = sorted(min_list, key=lambda x: x[0])

        domain_temp = {domain: [] for domain in list(FaultDomain)}
        for i in range(len(min_list)):
            current_domain = LogcatUtil.get_type_of_bug_key(min_list[i][1])
            domain_temp[FaultDomain.E_all].append(min_list[i][0])
            if current_domain == FaultDomain.E_all:
                continue
            domain_temp[FaultDomain.E_plus].append(min_list[i][0])
            if current_domain == FaultDomain.E_plus:
                continue
            domain_temp[FaultDomain.Vital].append(min_list[i][0])
            if current_domain == FaultDomain.Vital:
                continue
            domain_temp[FaultDomain.Fatal].append(min_list[i][0])

        for domain, time_list in domain_temp.items():
            time_list = sorted(time_list)
            res.loc[item_name, f"{domain.value}-n"] = len(time_list)
            for i in target_per_list:
                if len(time_list) == 0:
                    res.loc[item_name, f"{domain.value}-{i}%"] = 0
                else:
                    pos = math.floor(len(time_list) * i / 100) - 1
                    if pos < 0:
                        res.loc[item_name, f"{domain.value}-{i}%"] = 0
                    else:
                        res.loc[item_name, f"{domain.value}-{i}%"] = time_list[pos] / 3600
        return res


def present_fault_convergence_result(postfix: str, target_apps):
    result_dir_path = ExcelDirectoryPathGenerator.get_time_data_dir(DataType.Bug)

    excel_writer = pd.ExcelWriter(os.path.join(result_dir_path, "fault_time_convergence_data.xlsx"))

    for pattern, res_name in Experiments.TAG_PATTERN_DICT.items():
        if "combodroid" in pattern:
            current_target_apps = list(set(target_apps).intersection(set(empirical_app_list_all_for_combodroid)))
        else:
            current_target_apps = target_apps

        abstract_dict = FaultConvergenceTime.read_pickled_abstract_dict(DataType.Bug, pattern, postfix)
        current_target_apps = sorted(current_target_apps, key=lambda x: SORTED_APP_NAME_LIST_BY_INSTRUCTION.index(x.value))

        res = pd.DataFrame()

        for current_app in current_target_apps:
            time_list = FaultConvergenceTime.abstract_dict_to_min_list(abstract_dict, [current_app.value])
            current_res = FaultConvergenceTime.calculate_fault_discover_time(current_app.value, time_list)
            res = pd.concat([res, current_res], axis=0)

        res = add_statistical_data(res, float)

        # large_apps = current_target_apps[:len(current_target_apps) // 2]
        # small_apps = current_target_apps[len(current_target_apps) // 2:]
        #
        # for current_apps, app_postfix in [(large_apps, "L"), (small_apps, "S"), (current_target_apps, "All")]:
        #     time_list = FaultConvergenceTime.abstract_dict_to_min_list(abstract_dict,
        #                                                                [app.value for app in current_apps])
        #     current_res = FaultConvergenceTime.calculate_fault_discover_time(f"{res_name}-{app_postfix}", time_list)
        #     res = pd.concat([res, current_res], axis=0)


        res = res.apply(lambda x: x.apply(lambda y: "%.2f" % y) if x.dtype == float else x)
        # for column in res.columns:
        #     if column.endswith('n'):
        #         res[column] = res[column].astype(int)
        res.to_excel(excel_writer, sheet_name=f"{pattern}_{postfix}")

    excel_writer.save()
