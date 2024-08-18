# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import os
from typing import Optional, List

from android_testing_utils.log import my_logger
from evaluation.result_analyzer.analysis.correlation_analysis import Correlation
from evaluation.result_analyzer.analysis.significance_analysis import Significance
from evaluation.result_analyzer.analysis.variation_analysis import Variation
from evaluation.result_analyzer.utils.data_util import DataType
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator
from runtime_collection import unified_testing_config


class Experiments:
    APP_TARGETS = [
        (unified_testing_config.empirical_app_list_all, ""),
        (unified_testing_config.empirical_app_list_all_act_ge_50, "-ge50"),
        (unified_testing_config.empirical_app_list_all_act_ge_35, "-ge35"),
        (unified_testing_config.empirical_app_list_all_act_ge_20, "-ge20"),
        (unified_testing_config.empirical_app_list_all_act_ge_10_lt_20, "-ge10lt20"),
        (unified_testing_config.empirical_app_list_all_act_lt_10, "-lt10"),
    ]
    TIME_TARGETS = [
        (1800, 10800, f"0.5h"),
        (3600, 10800, f"1.0h"),
        (5400, 10800, f"1.5h"),
        (7200, 10800, f"2.0h"),
        (9000, 10800, f"2.5h"),
        (10800, 10800, f"3.0h"),
    ]
    EXPERIMENTAL_TARGETS = {
        DataType.Coverage: [
            (TIME_TARGETS, APP_TARGETS[:1]),
        ],
        DataType.Bug: [
            (TIME_TARGETS, APP_TARGETS[:1])
            # (TIME_TARGETS[-1:], APP_TARGETS[:1])
        ],
    }
    TAG_PATTERN_DICT = {
        "empirical-0816-monkey~": "Monkey",
        "empirical-0816-stoat~": "Stoat",
        "empirical-0816-ape~": "APE",
        # "empirical-0816-combodroid~": "Combodroid",
        # "empirical-0816-humanoid~": "Humanoid",
        # "empirical-08162-qt~": "QT",
        # "empirical-0816-ares~": "ARES",
        # "empirical-08162-dqt~": "DQT",
    }
    EXPERIMENTAL_APP_DICT = {
        "empirical-0816-ape~": unified_testing_config.empirical_app_list_all,
        "empirical-0816-ares~": unified_testing_config.empirical_app_list_all,
        "empirical-0816-combodroid~": unified_testing_config.empirical_app_list_all_for_combodroid,
        "empirical-0816-humanoid~": unified_testing_config.empirical_app_list_all,
        "empirical-0816-monkey~": unified_testing_config.empirical_app_list_all,
        "empirical-0816-stoat~": unified_testing_config.empirical_app_list_all,
        "empirical-08162-qt~": unified_testing_config.empirical_app_list_all,
        "empirical-08162-dqt~": unified_testing_config.empirical_app_list_all,
    }

    @classmethod
    def process_all_significance_data(cls, data_type: DataType):
        for time_targets, app_targets in cls.EXPERIMENTAL_TARGETS[data_type]:
            for app_list, app_postfix in app_targets:
                for target_time, total_test_time, time_postfix in time_targets:
                    postfix = f"{time_postfix}{app_postfix}"
                    my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Processing {data_type.value} data with postfix [{postfix}]...")
                    FullProcess.full_process_from_original_data_to_final_statistics_data(
                        data_type=data_type,
                        compare_tools=list(cls.TAG_PATTERN_DICT.values()),
                        postfix=postfix,
                    )

    @classmethod
    def get_all_cv_data(cls, data_type: DataType):
        postfix = "3.0h"
        my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Processing {data_type.value} data with postfix [{postfix}]...")
        FullProcess.full_process_from_original_data_to_cv_data(
            data_type=data_type,
            compare_tools=list(cls.TAG_PATTERN_DICT.values()),
            slicing_list=list(range(3, 11)),
            raw_postfix=postfix,
        )

    @classmethod
    def get_correlation_between_times(cls, data_type: DataType):
        my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Start calculating correlation between times...")
        app_postfix = cls.APP_TARGETS[0][1]
        time_postfix_list = [item[2] for item in cls.TIME_TARGETS]
        post_fix_list = [(f"{item}{app_postfix}", f"{time_postfix_list[-1]}{app_postfix}") for item in time_postfix_list]
        Correlation.get_correlation_between_time(post_fix_list, app_postfix, data_type)


class FullProcess:
    @classmethod
    def full_process_from_original_data_to_final_statistics_data(
        cls,
        data_type: DataType,
        compare_tools,
        postfix=None,
    ):
        my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Start calculating statistics data from raw data with {postfix}!")

        my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, "Step 1: calculating raw statistics data ...")
        Significance.original_data_to_raw_significance_data(
            original_data_path=os.path.join(ExcelDirectoryPathGenerator.get_original_data_dir(data_type), f"{data_type.value}_full_data{'' if postfix is None else '_' + postfix}.xlsx"),
            tools=compare_tools,
            data_type=data_type,
            postfix=postfix,
        )

        my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, "Step 2: processing statistics data ...")
        Significance.full_significance_process_for_spssau_raw_data_all_tool_pairs(
            file_name_to_write=f"{data_type.value}_ALL_TOOL_PAIRS",
            tools=compare_tools,
            data_type=data_type,
            postfix=postfix,
        )

        my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, "Step 3: calculating correlation between matrices ...")
        Correlation.get_correlation_between_metrics(f"{data_type.value}_ALL_TOOL_PAIRS{'' if postfix is None else '_' + postfix}.xlsx", data_type)

    @classmethod
    def full_process_from_original_data_to_cv_data(
            cls,
            data_type: DataType,
            compare_tools,
            slicing_list: Optional[List[int]] = None,
            raw_postfix=None,
    ):
        raw_data_file_path = os.path.join(ExcelDirectoryPathGenerator.get_original_data_dir(data_type), f"{data_type.value}_full_data{'' if raw_postfix is None else '_' + raw_postfix}.xlsx")
        if slicing_list is not None:
            for slicing in slicing_list:
                new_postfix = f"{''if raw_postfix is None else raw_postfix + '-'}{slicing}"
                my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Start calculating CV data from raw data with {raw_postfix} to {new_postfix}!")
                Variation.original_data_to_cv_data(
                    original_data_path=raw_data_file_path,
                    tools=compare_tools,
                    data_type=data_type,
                    slicing=slicing,
                    postfix=new_postfix,
                )

            my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, "Start combining CV data ...")
            Variation.combine_cv_avg_data(
                file_prefix=f"{data_type.value}_{''if raw_postfix is None else raw_postfix + '-'}",
                slicing_list=slicing_list,
            )
        else:
            my_logger.hint(my_logger.LogLevel.INFO, cls.__name__, True, f"Start calculating CV data from raw data with {raw_postfix}!")
            Variation.original_data_to_cv_data(
                original_data_path=raw_data_file_path,
                tools=compare_tools,
                data_type=data_type,
                postfix=raw_postfix,
            )
