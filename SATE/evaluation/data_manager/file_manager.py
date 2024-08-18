# ----------------------
# @Time  : 2023 Aug
# @Author: Yuanhong Lan
# ----------------------
import os
import shutil
from typing import Dict, List, NamedTuple, Tuple
from enum import Enum

import numpy as np

from android_testing_utils.log import my_logger
from constant.platform_constant import PlatformConstant
from runtime_collection.collector_util.util_coverage import ApkSourceCodeArgs, CoverageItem
from runtime_collection import unified_testing_config
from evaluation.result_analyzer.utils.pattern_util import PatternUtil


class TestResultType(Enum):
    ECFile = "ec_file"

    Log = "log"
    LogcatBug = "logcat_bug"
    AnrBug = "anr_bug"
    CoverageData = "coverage_data"


class NeedIdentifier(NamedTuple):
    need_log: bool
    need_logcat_bug: bool
    need_anr_bug: bool
    need_coverage_data: bool


class FileManagerUtil:
    @staticmethod
    def __add_targets_via_root_tag_file(root_dir_path: str, tag: str, target_apps: List[unified_testing_config.Apps], target_apps_str: List[str]) -> List[str]:
        res = []
        target_dir = os.path.join(root_dir_path, tag)
        if os.path.exists(target_dir):
            if target_apps is not None:
                for file_name in os.listdir(target_dir):
                    if file_name.split('_')[0] in target_apps_str:
                        res.append(os.path.join(target_dir, file_name))
            else:
                res.append(target_dir)
        return res

    @staticmethod
    def __add_targets_via_root_tag_package(root_dir_path: str, tag: str, target_apps: List[unified_testing_config.Apps], target_apps_package: List[str]) -> List[str]:
        res = []
        if target_apps is not None:
            for package in target_apps_package:
                target_dir = os.path.join(root_dir_path, tag, package)
                if os.path.exists(target_dir):
                    res.append(target_dir)
        else:
            target_dir = os.path.join(root_dir_path, tag)
            if os.path.exists(target_dir):
                res.append(target_dir)
        return res

    @staticmethod
    def __add_targets_via_root_package_tag(root_dir_path: str, tag: str, target_apps: List[unified_testing_config.Apps], target_apps_package: List[str]) -> List[str]:
        res = []
        if target_apps is not None:
            for package in target_apps_package:
                target_dir = os.path.join(root_dir_path, package, tag)
                if os.path.exists(target_dir):
                    res.append(target_dir)
        else:
            for app in os.listdir(root_dir_path):
                target_dir = os.path.join(root_dir_path, app, tag)
                if os.path.exists(target_dir):
                    res.append(target_dir)
        return res

    @staticmethod
    def check_target_dict(target_dict: Dict[TestResultType, List], prompt: str):
        my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False,
                       f"The following [{FileManagerUtil.count_targets(target_dict)}] dirs(files) will {prompt}!")
        for test_result_type, targets in target_dict.items():
            my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"    {test_result_type}:")
            for i in range(len(targets)):
                target = targets[i]
                my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"    {i+1}\t {target}")

        s = input(f"Confirm? (y/n) ")
        if s != 'y':
            my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, "Process exit!")
            exit()

    @staticmethod
    def remove_targets_in_target_dict(target_dict: Dict[TestResultType, List[str]]):
        for test_result_type, targets in target_dict.items():
            my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Remove for {test_result_type}")
            for target in targets:
                if os.path.exists(target):
                    my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"    Remove {target}")
                    if os.path.isfile(target):
                        os.remove(target)
                    else:
                        shutil.rmtree(target)

    @staticmethod
    def count_targets(target_dict: Dict[TestResultType, List[str]]) -> int:
        count = 0
        for key, value in target_dict.items():
            count += len(value)
        return count

    @staticmethod
    def is_empty_target_dict(targets: Dict[TestResultType, List[str]]) -> bool:
        return FileManagerUtil.count_targets(targets) == 0

    @staticmethod
    def get_move_target_dict_from_raw_target_dict(
            raw_target_dict: Dict[TestResultType, List[str]],
            source_path_key: str,
            destination_path_key: str,
            tag_pair: Tuple[str, str] = None,
    ) -> Dict[TestResultType, List[Tuple[str, str]]]:
        res = {}
        for test_result_type, targets in raw_target_dict.items():
            res[test_result_type] = []
            for target in targets:
                if not os.path.exists(target):
                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Target {target} does not exist!")
                    continue
                if not target.startswith(source_path_key):
                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Target {target} does not start with {source_path_key}!")
                    continue
                destination_path = target.replace(source_path_key, destination_path_key, 1)
                if tag_pair is not None:
                    destination_path = destination_path.replace(tag_pair[0], tag_pair[1])
                res[test_result_type].append((target, destination_path))
        return res

    @staticmethod
    def move_with_move_target_dict(move_target_dict: Dict[TestResultType, List[Tuple[str, str]]], is_copy: bool = False):
        for test_result_type, targets in move_target_dict.items():
            my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"{'Move' if not is_copy else 'Copy'} for {test_result_type}")
            for i in range(len(targets)):
                target = targets[i]
                source_path, destination_path = target
                if os.path.exists(source_path):
                    my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"    {i+1}\t {'Moving' if not is_copy else 'Copying'} from {source_path} to {destination_path}")
                    if os.path.exists(destination_path):
                        my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Destination {destination_path} already exists!")
                        continue
                    if not is_copy:
                        shutil.move(source_path, destination_path)
                    else:
                        if not os.path.exists(os.path.dirname(destination_path)):
                            os.makedirs(os.path.dirname(destination_path))
                        if os.path.isfile(source_path):
                            shutil.copy(source_path, destination_path)
                        else:
                            shutil.copytree(source_path, destination_path)

    @staticmethod
    def search_for_all_ec_dirs() -> List[str]:
        res = []
        for app, args in unified_testing_config.APK_SOURCE_CODE_ARGS_DICT.items():
            app: unified_testing_config.Apps
            args: ApkSourceCodeArgs
            ec_dir = os.path.join(args.root_path, args.build_relative_path, "./outputs/code-coverage")
            if os.path.exists(ec_dir):
                res.append(ec_dir)
        return res

    @staticmethod
    def search_for_all_experimental_target_dict(
            tag: str,
            target_apps: List[unified_testing_config.Apps] = None,
            need_identifier: NeedIdentifier = NeedIdentifier(True, True, True, True),
            replace_rule: Tuple[str, str] = None,
    ) -> Dict[TestResultType, List[str]]:

        target_apps_str = None
        target_apps_package = None
        if target_apps is not None:
            target_apps_str = [str(item) for item in target_apps]
            target_apps_package = [unified_testing_config.APK_SOURCE_CODE_ARGS_DICT[item].apk_package for item in target_apps]

        log_dir = PlatformConstant.TOOL_LOG_ROOT_DIR
        logcat_bug_dir = PlatformConstant.LOGCAT_BUG_ROOT_DIR
        anr_bug_dir = PlatformConstant.ANR_BUG_ROOT_DIR
        data_dir = PlatformConstant.COVERAGE_DATA_ROOT_DIR
        if replace_rule is not None:
            log_dir = log_dir.replace(replace_rule[0], replace_rule[1])
            logcat_bug_dir = logcat_bug_dir.replace(replace_rule[0], replace_rule[1])
            anr_bug_dir = anr_bug_dir.replace(replace_rule[0], replace_rule[1])
            data_dir = data_dir.replace(replace_rule[0], replace_rule[1])

        res = {}

        if need_identifier.need_log:
            res[TestResultType.Log] = FileManagerUtil.__add_targets_via_root_tag_file(log_dir, tag, target_apps, target_apps_str)

        if need_identifier.need_logcat_bug:
            res[TestResultType.LogcatBug] = FileManagerUtil.__add_targets_via_root_tag_file(logcat_bug_dir, tag, target_apps, target_apps_str)

        if need_identifier.need_anr_bug:
            res[TestResultType.AnrBug] = FileManagerUtil.__add_targets_via_root_tag_package(anr_bug_dir, tag, target_apps, target_apps_package)

        if need_identifier.need_coverage_data:
            res[TestResultType.CoverageData] = FileManagerUtil.__add_targets_via_root_package_tag(data_dir, tag, target_apps, target_apps_package)

        return res

    @staticmethod
    def recursively_search_for_empty_dirs(current_dir_path: str) -> List:
        if not os.path.isdir(current_dir_path):
            return []
        if len(os.listdir(current_dir_path)) == 0:
            return [current_dir_path]
        res = []
        for file in os.listdir(current_dir_path):
            res.extend(FileManagerUtil.recursively_search_for_empty_dirs(os.path.join(current_dir_path, file)))
        return res


class Remove:
    @staticmethod
    def remove_with_tag_list(tag_list: List[str], target_apps: List[unified_testing_config.Apps] = None):
        for tag in tag_list:
            my_logger.new_line()

            target_dict = FileManagerUtil.search_for_all_experimental_target_dict(tag, target_apps)

            if FileManagerUtil.is_empty_target_dict(target_dict):
                my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Nothing to remove for tag {tag}!")
                continue

            FileManagerUtil.check_target_dict(target_dict, "remove")

            FileManagerUtil.remove_targets_in_target_dict(target_dict)

    @staticmethod
    def clean_all_ec_under_app_source_code():
        target_dict = {TestResultType.ECFile: FileManagerUtil.search_for_all_ec_dirs()}
        FileManagerUtil.check_target_dict(target_dict, "clean")
        FileManagerUtil.remove_targets_in_target_dict(target_dict)


class Move:
    @staticmethod
    def move_with_tag_list(
            tag_list: List[str],
            default_path_prefix: str,
            source_path_key: str,
            destination_path_key: str,
            target_apps: List[unified_testing_config.Apps] = None,
            is_copy: bool = False,
    ):
        assert source_path_key != destination_path_key

        for tag in tag_list:
            my_logger.new_line()

            target_dict = FileManagerUtil.search_for_all_experimental_target_dict(
                tag, target_apps, replace_rule=(default_path_prefix, source_path_key)
            )

            if FileManagerUtil.is_empty_target_dict(target_dict):
                my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Nothing to {'move' if not is_copy else 'copy'} for tag {tag}!")
                return

            move_target_dict = FileManagerUtil.get_move_target_dict_from_raw_target_dict(target_dict, source_path_key, destination_path_key)

            FileManagerUtil.check_target_dict(move_target_dict, f"{'move' if not is_copy else 'copy'}")

            FileManagerUtil.move_with_move_target_dict(move_target_dict, is_copy=is_copy)

    @classmethod
    def move_with_tag_dict(
            cls,
            tag_dict: Dict[str, str],
            default_path_prefix: str,
            source_path_key: str,
            destination_path_key: str,
            target_apps: List[unified_testing_config.Apps] = None,
            is_copy: bool = False,
    ):
        for raw_tag, target_tag in tag_dict.items():
            my_logger.new_line()

            target_dict = FileManagerUtil.search_for_all_experimental_target_dict(
                raw_tag, target_apps, replace_rule=(default_path_prefix, source_path_key)
            )

            if FileManagerUtil.is_empty_target_dict(target_dict):
                my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Nothing to {'move' if not is_copy else 'copy'} for tag pair {raw_tag} -> {target_tag}!")
                return

            move_target_dict = FileManagerUtil.get_move_target_dict_from_raw_target_dict(
                target_dict, source_path_key, destination_path_key, (raw_tag, target_tag)
            )

            FileManagerUtil.check_target_dict(move_target_dict, f"{'move' if not is_copy else 'copy'}")

            FileManagerUtil.move_with_move_target_dict(move_target_dict, is_copy=is_copy)


class Rename:
    @classmethod
    def rename_tag(cls, old_tag: str, new_tag: str):
        targets = FileManagerUtil.search_for_all_experimental_target_dict(tag=old_tag)
        print()


class Check:
    @staticmethod
    def check_all_coverage_data(tag_pattern: str = None, ignore_pattern: str = None, testing_time: int = None):
        if tag_pattern is not None:
            PatternUtil.is_pattern_valid(tag_pattern)
            my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Check coverage data with tag pattern [{tag_pattern}]")

        if ignore_pattern is not None:
            PatternUtil.is_pattern_valid(ignore_pattern)
            my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Check coverage data with ignore pattern [{ignore_pattern}]")

        pass_count = 0
        total_count = 0

        coverage_data_root_dir = PlatformConstant.COVERAGE_DATA_ROOT_DIR
        for package in os.listdir(coverage_data_root_dir):
            package_data_dir = os.path.join(coverage_data_root_dir, package)
            for tag in os.listdir(package_data_dir):
                if tag[-2] == '@' or tag[-3] == '@':
                    continue

                if tag_pattern is not None:
                    if not PatternUtil.is_match(tag_pattern, tag):
                        continue
                    if (ignore_pattern is not None) and PatternUtil.is_match(ignore_pattern, tag):
                        continue

                total_count += 1
                has_check = False
                has_warning = False

                tag_data_dir = os.path.join(package_data_dir, tag)

                file_count = len(os.listdir(tag_data_dir))
                if file_count < 4:
                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] has LESS than 4 files!")
                    has_warning = True
                elif file_count > 4:
                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] has MORE than 4 files!")
                    has_warning = True

                for file in os.listdir(tag_data_dir):
                    if ('Jacoco' in file) and ('npy' in file):
                        has_check = True
                        file_path = os.path.join(tag_data_dir, file)
                        data: Dict[str, List[CoverageItem]] = np.load(file_path, allow_pickle=True).item()
                        for key, value in data.items():
                            if len(value) == 0:
                                my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] type [{key}] has empty data!")
                                has_warning = True
                                break

                            if package in [
                                unified_testing_config.APK_SOURCE_CODE_ARGS_DICT[unified_testing_config.Apps.APhotoManager].apk_package,
                            ]:
                                threshold = 0.3
                            else:
                                threshold = 0.2

                            if (key == 'INSTRUCTION') and (value[0].detail.rate > threshold):
                                my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] type [{key}] has its start coverage rate > {threshold}!")
                                has_warning = True

                            former_covered = value[0].detail.covered
                            former_total = value[0].detail.total
                            for i in range(1, len(value)):
                                item = value[i]
                                if item.detail.covered < former_covered:
                                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] type [{key}] has coverage decrease!")
                                    has_warning = True
                                    break
                                if item.detail.total != former_total:
                                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] type [{key}] has total inconsistent!")
                                    has_warning = True
                                    break
                                former_covered = item.detail.covered
                                former_total = item.detail.total
                            if (testing_time is not None) and (value[-1].time < testing_time):
                                my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] type [{key}] has its final time {value[-1].time} < {testing_time}!")
                                has_warning = True
                        break

                if not has_check:
                    my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Package [{package}] tag [{tag}] has no jacoco coverage data!")
                    has_warning = True

                if not has_warning:
                    pass_count += 1
                    my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Package [{package}] tag [{tag}] passed!")

        my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Total [{total_count}] checked, [{pass_count}] passed, [{total_count - pass_count}] may have problem!")

    @classmethod
    def check_app_by_log(cls, target_tag: str, full_app_list: List[unified_testing_config.Apps] = None):
        log_dir = os.path.join(PlatformConstant.TOOL_LOG_ROOT_DIR, target_tag)
        app_list = [unified_testing_config.Apps[item.split('_')[0].split('.')[1]] for item in os.listdir(log_dir)]
        if full_app_list is None:
            return app_list
        else:
            return list(set(full_app_list) - set(app_list))

    @classmethod
    def check_experimental_data_availability(
            cls,
            target_tag_app_dict: Dict[str, List[unified_testing_config.Apps]],
            need_identifier: NeedIdentifier = NeedIdentifier(True, True, True, True),
    ):
        total_count = 0
        pass_count = 0

        for tag, apps in target_tag_app_dict.items():
            for app in apps:
                temp_target_dict = FileManagerUtil.search_for_all_experimental_target_dict(tag, [app], need_identifier)
                has_problem = False
                check_dict = {
                    "need_log": TestResultType.Log,
                    "need_logcat_bug": TestResultType.LogcatBug,
                    "need_anr_bug": TestResultType.AnrBug,
                    "need_coverage_data": TestResultType.CoverageData,
                }
                for need_filed, res_type in check_dict.items():
                    if getattr(need_identifier, need_filed) and len(temp_target_dict[res_type]) != 1:
                        my_logger.hint(my_logger.LogLevel.WARNING, "FileManager", False, f"Tag [{tag}] app [{app}] has no {res_type.value}!")
                        has_problem = True
                if not has_problem:
                    my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Tag [{tag}] app [{app}] passed!")
                    pass_count += 1
                total_count += 1

        my_logger.hint(my_logger.LogLevel.INFO, "FileManager", False, f"Total [{total_count}] checked, [{pass_count}] passed, [{total_count - pass_count}] may have problem!")


if __name__ == '__main__':
    remove_list = [
        ("empirical-0816-ape@10", None),
        ("empirical-0816-ares@10", None),
        ("empirical-0816-monkey@10", None),
        ("empirical-0816-qt@10", None),
        ("empirical-0816-stoat@10", None),
    ]
    for tag, apps in remove_list:
        Remove.remove_with_tag_list(
            tag_list=[tag],
            target_apps=apps,
        )

    # Remove.clean_all_ec_under_app_source_code()

    # Move.move_with_tag_list(
    #     tag_list=["empirical-0816-humanoid-10"],
    #     default_path_prefix="/DATA/experimental_results",
    #     source_path_key="/DATA/experimental_results",
    #     destination_path_key="/DATA/experimental_results_new",
    #     target_apps=[unified_testing_config.Apps.Signal],
    #     is_copy=True,
    # )
    # Move.move_with_tag_dict(
    #     tag_dict={f"empirical-0816-dqt-{i}": f"empirical-08162-dqt-{i}" for i in range(1, 11)},
    #     default_path_prefix="/DATA/experimental_results",
    #     source_path_key="/DATA/previous_results",
    #     destination_path_key="/DATA/previous_results",
    # )

    # Check.check_all_coverage_data(
    #     tag_pattern="empirical-0816~",
    # )

    # from result_analyzation.analyzer_util import Experiments
    # current_target_tag_app_dict = {}
    # for prefix, app_list in Experiments.EXPERIMENTAL_APP_DICT.items():
    #     current_target_tag_app_dict.update({f"{prefix}-{i}": app_list for i in range(1, 11)})
    # Check.check_experimental_data_availability(current_target_tag_app_dict)

    # for app in Check.check_app_by_log("empirical-08162-qt-4"):
    #     print(f"unified_testing_config.{app},")

    # Rename.rename_tag("empirical-08162-qt-1", "empirical-0816-qt-1")
