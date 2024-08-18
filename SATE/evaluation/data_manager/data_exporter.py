# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import os
from functools import partial
from typing import Dict, Optional, List, Set, Callable, Tuple

import numpy as np
import pandas as pd

from android_testing_utils.log import my_logger
from constant import PlatformConstant
from evaluation.result_analyzer.utils.fault_util import LogcatUtil, FaultDomain, AbstractItem, BugAnalyzer, FaultResUtil
from evaluation.result_analyzer.study_analyzer.study_util import Experiments
from evaluation.result_analyzer.utils.coverage_util import CoverageTimeUtil
from evaluation.result_analyzer.utils.data_util import DataType
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator, PathUtil
from evaluation.result_analyzer.utils.pattern_util import PatternUtil
from runtime_collection import unified_testing_config
from runtime_collection.collector_util.util_coverage import CoverageItem


class Export:
    @classmethod
    def export_excel_with_tag_pattern_dict(
            cls,
            tag_pattern_dict: Dict[str, str],
            target_apps: Optional[List[unified_testing_config.Apps]] = None,
            target_time: Optional[int] = None,
            total_testing_time: Optional[int] = None,
            output_file_postfix: Optional[str] = None,
            print_details: bool = False,
    ):
        tag_pattern_list = list(tag_pattern_dict.keys())

        excel_writer = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_original_data_dir(DataType.Coverage),
            f"coverage_raw_data{'_' + output_file_postfix if output_file_postfix is not None else ''}.xlsx"
        ))
        excel_writer_spss = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_original_data_dir(DataType.Coverage),
            f"coverage_full_data{'_' + output_file_postfix if output_file_postfix is not None else ''}.xlsx"
        ))
        all_data = pd.DataFrame()

        for package in os.listdir(PlatformConstant.COVERAGE_DATA_ROOT_DIR):
            if (target_apps is not None) and (unified_testing_config.get_app_by_package_name(package) not in target_apps):
                continue
            app_name = unified_testing_config.get_app_name_by_package_name(package)

            current_data = pd.DataFrame(columns=[
                "INSTRUCTION",
                "BRANCH",
                "LINE",
                "COMPLEXITY",
                "METHOD",
                "CLASS",
                "ACTIVITY",
            ])
            all_data = pd.concat([all_data, pd.DataFrame(columns=[
                f"{app_name}-INSTRUCTION",
                f"{app_name}-LINE",
                f"{app_name}-METHOD",
                f"{app_name}-ACTIVITY",
            ])])

            package_dir = os.path.join(PlatformConstant.COVERAGE_DATA_ROOT_DIR, package)

            for tag in os.listdir(package_dir):

                if '@' in tag or not PatternUtil.is_match_among_list(tag_pattern_list, tag):
                    continue

                tag_dir = os.path.join(PlatformConstant.COVERAGE_DATA_ROOT_DIR, package, tag)
                if len(os.listdir(tag_dir)) != 4:
                    my_logger.hint(my_logger.LogLevel.WARNING, "DataUtil", False, f"Not 4 items, Continue! {tag_dir}")
                    continue
                for file in os.listdir(tag_dir):
                    if file.endswith(".npy"):
                        temp_data: Dict[str, List[CoverageItem]] = np.load(os.path.join(tag_dir, file), allow_pickle=True).item()
                        for key, value in temp_data.items():
                            true_value = CoverageTimeUtil.get_appointed_time_coverage(value, target_time, total_testing_time)
                            current_data.loc[tag, key] = true_value

                            if tag[-3:-1] == '-p':
                                all_data_tag = tag[:-3]
                            else:
                                all_data_tag = tag
                            all_data_key = f"{app_name}-{key}"
                            if all_data_key in all_data.columns:
                                all_data.loc[all_data_tag, all_data_key] = true_value
            current_data.sort_index(
                inplace=True,
                key=lambda x: x.map(lambda y: ('-'.join(y.split('-')[:-1]), int(y.split('-')[-1])))
            )

            if print_details:
                my_logger.hint(my_logger.LogLevel.INFO, "Export", False,f"\n#############    {app_name}    ############# \n{current_data}")

            current_data.to_excel(excel_writer, sheet_name=app_name)

        excel_writer.save()

        all_data = all_data.fillna(-1)
        all_data.sort_index(
            inplace=True,
            key=lambda x: x.map(lambda y: ('-'.join(y.split('-')[:-1]), int(y.split('-')[-1])))
        )

        PatternUtil.rename_dataframe_by_tag_pattern_dict(all_data, tag_pattern_dict)
        all_data.to_excel(excel_writer_spss)

        excel_writer_spss.save()
        excel_writer_spss.close()


class CoverageExperiment:
    @classmethod
    def export_all_coverage_data(cls):
        for time_targets, app_targets in Experiments.EXPERIMENTAL_TARGETS[DataType.Coverage]:
            for app_list, app_postfix in app_targets:
                for target_time, total_test_time, time_postfix in time_targets:
                    postfix = f"{time_postfix}{app_postfix}"
                    my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Exporting coverage data with postfix [{postfix}]...")
                    Export.export_excel_with_tag_pattern_dict(
                        tag_pattern_dict=Experiments.TAG_PATTERN_DICT,
                        target_apps=app_list,
                        target_time=target_time,
                        total_testing_time=total_test_time,
                        output_file_postfix=postfix,
                    )


class BugExperiment:
    @classmethod
    def export_raw_bug(
            cls,
            pattern_dict: Dict[str, str],
            target_time: int = None,
            output_file_postfix: Optional[str] = None,
    ):
        excel_writer = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_original_data_dir(DataType.Bug),
            f"bug_raw_data{'_' + output_file_postfix if output_file_postfix is not None else ''}.xlsx"
        ))
        excel_writer_spss = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_original_data_dir(DataType.Bug),
            f"bug_full_data{'_' + output_file_postfix if output_file_postfix is not None else ''}.xlsx"
        ))

        all_abstract_data: Dict[str, Dict[str, Set[str]]] = {}
        all_data = pd.DataFrame()

        my_logger.hint(my_logger.LogLevel.INFO, "BugUtil", True, f"Start analyzing bug data ...")
        for pattern in pattern_dict.keys():
            abstract_dict: Dict[str, Dict[str, List[AbstractItem]]]
            combined_result: Dict[str, List[AbstractItem]]
            abstract_dict, combined_result = BugAnalyzer.analyze(
                app_str=None,
                pattern=pattern,
                tag_list=None,
                detail_level=0,
                show_each=False,
                show_final=False,
                target_time=target_time,
            )

            tag_name_list = list(set([PathUtil.get_tag_name_from_logcat_file_path(file_key) for file_key in abstract_dict.keys()]))
            app_name_list = list(set([PathUtil.get_app_name_from_logcat_file_path(file_key) for file_key in abstract_dict.keys()]))
            all_data = pd.concat([all_data, pd.DataFrame(index=tag_name_list, columns=[f"{app_name}-{bug_domain.value}" for app_name in app_name_list for bug_domain in FaultDomain])])

            for file_key, abstract_data in abstract_dict.items():
                tag_name = PathUtil.get_tag_name_from_logcat_file_path(file_key)
                app_name = PathUtil.get_app_name_from_logcat_file_path(file_key)

                if app_name not in all_abstract_data:
                    all_abstract_data[app_name] = {}
                all_abstract_data[app_name][tag_name] = set(abstract_data.keys())

                for bug_domain, count in LogcatUtil.get_num_of_different_bugs(abstract_data.keys()).items():
                    all_data.loc[tag_name, f"{app_name}-{bug_domain.value}"] = count

        my_logger.hint(my_logger.LogLevel.INFO, "BugUtil", True, f"Start counting extra bug data ...")

        def add_extra_data(current_app_data: Dict[str, Set[str]], identifier_func: Callable,
                           combine_group_func: Callable, prefix: str, write_back: bool = True):
            groups: Dict[List[Tuple[str, Set]]] = {}
            for tag_name, abstract_key_set in current_app_data.items():
                identifier = identifier_func(tag_name)
                if identifier not in groups:
                    groups[identifier] = []
                groups[identifier].append((tag_name, abstract_key_set))
            new_app_data = {}
            for identifier in groups.keys():
                groups[identifier] = combine_group_func(groups[identifier])
                for tag_name, combined_keys in groups[identifier]:
                    new_app_data[tag_name] = combined_keys
                    if write_back:
                        for bug_domain, count in LogcatUtil.get_num_of_different_bugs(combined_keys).items():
                            all_data.loc[tag_name, f"{app_name}-{prefix}{bug_domain.value}"] = count
            return new_app_data

        for app_name, app_data in all_abstract_data.items():
            unique_app_data = add_extra_data(
                app_data,
                lambda x: x.split('-')[-1],
                FaultResUtil.get_unique_bugs,
                "U",
            )
            combined_app_data3 = add_extra_data(
                app_data,
                lambda x: x.split('-')[-2],
                partial(FaultResUtil.get_combine_faults, k=3),
                "T3",
            )
            combined_app_data5 = add_extra_data(
                app_data,
                lambda x: x.split('-')[-2],
                partial(FaultResUtil.get_combine_faults, k=5),
                "T5",
            )
            # add_extra_data(
            #     combined_app_data,
            #     lambda x: x.split('-')[-1],
            #     FaultResUtil.get_unique_bugs,
            #     "AU",
            # )

        all_data = all_data.fillna(-1)
        all_data = all_data.astype(int)
        all_data.sort_index(
            inplace=True,
            key=lambda x: x.map(lambda y: ('-'.join(y.split('-')[:-1]), int(y.split('-')[-1])))
        )

        all_app_data = {}
        for column in all_data.columns:
            app_name = column.split('-')[0]
            current_line_data = pd.DataFrame(all_data[column], columns=[column])
            if app_name in all_app_data:
                all_app_data[app_name] = pd.concat([all_app_data[app_name], current_line_data], axis=1)
            else:
                all_app_data[app_name] = current_line_data

        for app_name, app_data in all_app_data.items():
            app_data.to_excel(excel_writer, sheet_name=app_name)

        excel_writer.save()

        PatternUtil.rename_dataframe_by_tag_pattern_dict(all_data, pattern_dict)
        all_data.to_excel(excel_writer_spss)

        excel_writer_spss.save()

    @classmethod
    def export_all_bug_data(cls):
        for time_targets, app_targets in Experiments.EXPERIMENTAL_TARGETS[DataType.Bug]:
            for app_list, app_postfix in app_targets:
                for target_time, total_test_time, time_postfix in time_targets:
                    postfix = f"{time_postfix}{app_postfix}"
                    my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Exporting fault data with postfix [{postfix}]...")
                    cls.export_raw_bug(
                        pattern_dict=Experiments.TAG_PATTERN_DICT,
                        target_time=target_time,
                        output_file_postfix=postfix,
                    )


# if __name__ == '__main__':
#     CoverageExperiment.export_all_coverage_data()
#     BugExperiment.export_all_bug_data()
