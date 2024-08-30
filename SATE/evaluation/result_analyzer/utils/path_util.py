# ----------------------
# @Time  : 2023 Mar
# @Author: Yuanhong Lan
# ----------------------
import os
from typing import Optional

from evaluation.result_analyzer.utils.data_util import DataType
from runtime_collection import unified_testing_config


class PathUtil:
    @staticmethod
    def get_tag_name_from_logcat_file_path(logcat_file_absolute_full_path: str):
        # "/home/root_running_data/testing_results/logcat_bug/Stoat-0609-uni-1/Apps.APhotoManager_2023-06-09-23:37:44_Stoat-0609-uni-1_bug.txt"
        # -> "Stoat-0609-uni-1"
        temp = logcat_file_absolute_full_path.split('/')[-2]
        # if temp[-2] == 'p':
        #     temp = temp[:-3]
        return temp

    @staticmethod
    def get_app_name_from_logcat_file_path(logcat_file_absolute_full_path: str):
        # "/home/root_running_data/testing_results/logcat_bug/Stoat-0609-uni-1/Apps.APhotoManager_2023-06-09-23:37:44_Stoat-0609-uni-1_bug.txt"
        # -> "APhotoManager"
        return logcat_file_absolute_full_path.split('/')[-1].split('_')[0].split('.')[1]

    @staticmethod
    def get_package_from_logcat_file_path(logcat_file_absolute_full_path: str):
        # "/home/root_running_data/testing_results/logcat_bug/Stoat-0609-uni-1/Apps.APhotoManager_2023-06-09-23:37:44_Stoat-0609-uni-1_bug.txt"
        # -> "de.k3b.android.androFotoFinder.debug"
        return unified_testing_config.APK_SOURCE_CODE_ARGS_DICT[
            unified_testing_config.Apps[PathUtil.get_app_name_from_logcat_file_path(logcat_file_absolute_full_path)]
        ].apk_package


class ExcelDirectoryPathGenerator:
    EXCEL_ROOT_PATH = os.path.join(os.path.dirname(__file__), "../excel")

    @classmethod
    def get_original_data_dir(cls, data_type: DataType):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, data_type.value, "1st_original_data")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_raw_statistic_data_dir(cls, data_type: DataType):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, data_type.value, "2nd_raw_statistic_data")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_processed_statistic_data_dir(cls, data_type: DataType):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, data_type.value, "3rd_processed_statistic_data")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_correlation_data_dir(cls):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, "correlation")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_cv_data_dir(cls):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, "cv")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_time_data_dir(cls, data_type: Optional[DataType]):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, "time")
        if data_type is not None:
            target_dir = os.path.join(target_dir, data_type.value)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_temp_dir(cls, data_type: DataType):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, "temp", data_type.value)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_pickle_data_dir(cls, data_type: DataType, postfix: str = None):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, "pickle", data_type.value, f"abstract{'' if postfix is None else f'_{postfix}'}")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    @classmethod
    def get_case_study_data_dir(cls):
        target_dir = os.path.join(cls.EXCEL_ROOT_PATH, "case_study")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir
