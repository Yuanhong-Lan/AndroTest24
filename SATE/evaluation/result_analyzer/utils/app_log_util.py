# ----------------------
# @Time  : 2022 May
# @Author: Yuanhong Lan
# ----------------------
import os.path
import re
import traceback
import pandas as pd

from typing import List, Union, Optional, Tuple, Dict
from enum import Enum

from constant.platform_constant import PlatformConstant


class AnalyzeType(Enum):
    KEYWORD = 1,
    PATTERN_ONE = 2,
    PATTERN_AVG = 3,


class AnalyzePattern:
    @staticmethod
    def analyze_one(analyze_type, pattern, analyze_target):
        func_map = {
            AnalyzeType.KEYWORD: AnalyzePattern.__find_occur_time,
            AnalyzeType.PATTERN_ONE: AnalyzePattern.__match_pattern_once,
            AnalyzeType.PATTERN_AVG: AnalyzePattern.__calculate_pattern_average,
        }
        return func_map[analyze_type](analyze_target, pattern)

    @staticmethod
    def __find_occur_time(s: str, pattern: str):
        return s.count(pattern)

    @staticmethod
    def __match_pattern_once(s: str, pattern: str):
        pattern = re.compile(pattern)
        res = re.findall(pattern, s)
        if len(res) > 1:
            raise Exception(f"Result should not more than one! Attention: {pattern}")
        elif len(res) == 0:
            return None
        else:
            return res[0]

    @staticmethod
    def __calculate_pattern_average(s: str, pattern: str):
        pattern = re.compile(pattern)
        match_res = [float(i) for i in re.findall(pattern, s)]
        if len(match_res) == 0:
            return 0
        else:
            return round(sum(match_res) / len(match_res), 2)


def analyze_one_file(file_path, pattern_list) -> List[str]:
    f = open(file_path, 'r')
    s = f.read()
    res = []

    for analyze_type, pattern in pattern_list:
        try:
            res.append(AnalyzePattern.analyze_one(analyze_type, pattern, s))
        except Exception:
            print(traceback.print_exc())
            print(f"Exception happened at {file_path}, with {analyze_type} {pattern}")
            res.append('_')
            continue
    return res


def analyze_one_app(
        apk_name: Optional[str],
        tag_list: List[str],
        pattern_list: List[Tuple[AnalyzeType, str]],
        print_result=False
) -> Dict[str, List[str]]:
    tag_list = sorted(tag_list)
    if apk_name is None:
        apk_name = input("Enter prefix: ")

    raw_data = {}

    for tag in tag_list:
        dir_path = os.path.join(PlatformConstant.TOOL_LOG_ROOT_DIR, tag)
        file_name = None
        for file in os.listdir(dir_path):
            if (file.startswith(apk_name)) and ('_log' in file):
                file_name = file
                break
        if file_name is None:
            continue
        file_path = os.path.join(dir_path, file_name)
        raw_data[tag] = analyze_one_file(file_path, pattern_list)

    if print_result:
        df = pd.DataFrame(
            data=raw_data,
            index=[item[1] for item in pattern_list],
        )
        print(df)

    return raw_data


def analyze_all_apps(tag_list: List[str], only_coverage=False):
    from runtime_collection.unified_testing_config import ALL_APPS_STR, Apps
    app_list = ALL_APPS_STR
    # app_list = [str(Apps.BookCatalogue)]

    if only_coverage:
        df = pd.DataFrame()
        for app in app_list:
            temp: Dict[str, List[str]] = analyze_one_app(app, tag_list, COVERAGE_ANALYZE_PATTERN, print_result=False)
            for tag, value in temp.items():
                df.loc[app, tag] = "%.2f" % (float(value[0]) * 100) if not pd.isna(value[0]) else value[0]
        print(df)
        df.to_excel("coverage.xlsx")
    else:
        for app in app_list:
            print(f"---------- {app} ----------")
            analyze_one_app(app, tag_list, ANALYZE_LIST, print_result=True)
            print()
            print()


def get_statistics_results(log_file_path, activity_coverage_file_path):
    res = {}
    statistics_from_log = {
        "total_tested_time": (AnalyzeType.PATTERN_ONE, "Max relative time is (\\d+)"),
        "final_instruction_coverage": (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nBRANCH\\n"),
        "final_branch_coverage": (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nLINE\\n"),
        "final_line_coverage": (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nCOMPLEXITY\\n"),
        "final_cyclomatic_complexity_coverage": (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nMETHOD\\n"),
        "final_method_coverage": (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nCLASS\\n"),
        "final_class_coverage": (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nLogLevel\\.INFO"),
    }
    log_keys = list(statistics_from_log.keys())
    log_values = analyze_one_file(log_file_path, list(statistics_from_log.values()))
    for i in range(len(log_keys)):
        res[log_keys[i]] = log_values[i]

    statistics_from_activity_data = {
        "total_tested_activities": (AnalyzeType.PATTERN_ONE, "Activity Coverage: (\\d+)/"),
        "final_activity_coverage": (AnalyzeType.PATTERN_ONE, "Activity Coverage: \\d+/\\d+  (0\\.\\d+)"),
    }
    activity_keys = list(statistics_from_activity_data.keys())
    activity_values = analyze_one_file(activity_coverage_file_path, list(statistics_from_activity_data.values()))
    for i in range(len(activity_keys)):
        res[activity_keys[i]] = activity_values[i]

    # for key, value in res.items():
    #     print(f"{key}: {value}")
    return res


ANALYZE_LIST = [
    (AnalyzeType.PATTERN_ONE, "rate=(0\\.\\d+)\\)\\nBRANCH\\n"),
    # (AnalyzeType.PATTERN_ONE, "Current mode: (\\S+)"),

    (AnalyzeType.PATTERN_ONE, "Testing finished at .*step (\\d+)"),
    (AnalyzeType.PATTERN_ONE, "Total normal event count: (\\d+)"),
    (AnalyzeType.PATTERN_ONE, "Total system event count: (\\d+)"),
    (AnalyzeType.PATTERN_ONE, "Total other .*step count: (\\d+)"),

    # (AnalyzeType.KEYWORD, "Catch null! Focus info"),
    # (AnalyzeType.KEYWORD, "Wait for focus to be not null, time cost"),
    # (AnalyzeType.PATTERN_AVG, "Wait for focus to be not null, time cost (\\d+\\.?\\d+)s"),

    (AnalyzeType.KEYWORD, "Is not responding! Check by current focus"),
    (AnalyzeType.KEYWORD, "Is asking permission! Check by current focus"),

    # (AnalyzeType.KEYWORD, "Clean App Data"),
    # (AnalyzeType.KEYWORD, "Force Stop"),
    # (AnalyzeType.KEYWORD, "Restart APP"),
    #
    # (AnalyzeType.KEYWORD, "Checking network"),
    # (AnalyzeType.KEYWORD, "Shutdown network"),
    #
    # (AnalyzeType.KEYWORD, "Dumpsys UNKNOWN"),
    # (AnalyzeType.KEYWORD, "Dumpsys need attention"),

    # (AnalyzeType.KEYWORD, "Current package is UNKNOWN, wait. Continue"),

    # (AnalyzeType.KEYWORD, "Drop out of the app, back try 1 time"),
    # (AnalyzeType.KEYWORD, "Drop out of the app, back try 2 time"),
    # (AnalyzeType.KEYWORD, "Reopen APP"),
    # (AnalyzeType.KEYWORD, "Drop out of the app, restart"),
    # (AnalyzeType.PATTERN_AVG, "Drop out of the app, restart! Sleep (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "May get stuck, run monkey"),

    # (AnalyzeType.PATTERN_AVG, "Current epsilon: (\\d+\\.?\\d*)"),

    (AnalyzeType.KEYWORD, "Handle redundant view with"),
    (AnalyzeType.KEYWORD, "More than 20, need handle"),
    (AnalyzeType.KEYWORD, "Too homogeneous, need handle"),
    (AnalyzeType.KEYWORD, "Not homogeneous, continue"),

    # (AnalyzeType.KEYWORD, "Executing event: dump to"),
    # (AnalyzeType.PATTERN_AVG, "Function dump_to_file cost time: (\\d+\\.?\\d*)s"),
    (AnalyzeType.KEYWORD, "Dump time out, need attention"),
    (AnalyzeType.KEYWORD, "Uiautomator.JsonRPCError, need attention"),
    (AnalyzeType.KEYWORD, "Continuous dump error, run monkey"),
    (AnalyzeType.KEYWORD, "Continuous dump error, reopen app"),
    (AnalyzeType.KEYWORD, "Continuous dump error, restart app"),

    # (AnalyzeType.KEYWORD, "State cache hit"),
    # (AnalyzeType.KEYWORD, "State cache miss"),

    # (AnalyzeType.KEYWORD, "Exception: [Warning] The tree for EventExtractor should not be empty"),
    # (AnalyzeType.KEYWORD, "Exception: [Warning] There should not be no extracted action to execute"),
    (AnalyzeType.KEYWORD, "Something wrong, continue"),
    (AnalyzeType.KEYWORD, "Continuous extract error, run monkey"),
    (AnalyzeType.KEYWORD, "Continuous extract error, reopen app"),
    (AnalyzeType.KEYWORD, "Continuous extract error, restart app"),

    # (AnalyzeType.KEYWORD, "Add penalty when exit"),
    # (AnalyzeType.KEYWORD, "Add penalty when no change"),
    # (AnalyzeType.KEYWORD, "Empty dqn temp"),
    # (AnalyzeType.KEYWORD, "Train network when exit on training step"),
    # (AnalyzeType.KEYWORD, "Train network normal on training step"),

    (AnalyzeType.KEYWORD, "--Event selection mode-- SYSTEM-Monkey"),
    (AnalyzeType.KEYWORD, "--Event selection mode-- SYSTEM-Trigger"),
    (AnalyzeType.KEYWORD, "--Event selection mode-- SYSTEM-Random"),
    (AnalyzeType.KEYWORD, "--Event selection mode-- RANDOM (by epsilon)"),
    (AnalyzeType.KEYWORD, "--Event selection mode-- RANDOM (by force)"),
    (AnalyzeType.KEYWORD, "--Event selection mode-- MAX"),
    # (AnalyzeType.KEYWORD, "Q-values are all the same, use weighted random"),

    # (AnalyzeType.KEYWORD, "Reward: exit"),
    # (AnalyzeType.KEYWORD, "Reward: New activity same"),
    # (AnalyzeType.KEYWORD, "Reward: New activity true"),
    # (AnalyzeType.KEYWORD, "Reward: Total new state"),
    # (AnalyzeType.KEYWORD, "Reward: Partial new state"),
    # (AnalyzeType.KEYWORD, "Reward: New pair same"),
    # (AnalyzeType.KEYWORD, "Reward: New pair jump"),
    # (AnalyzeType.KEYWORD, "Reward: Total new pair"),
    # (AnalyzeType.KEYWORD, "Reward: No change"),
    # (AnalyzeType.KEYWORD, "Reward: Too similar"),
    # (AnalyzeType.KEYWORD, "Reward: Normal situation"),
    #
    # (AnalyzeType.KEYWORD, " B_-"),
    # (AnalyzeType.KEYWORD, " A_-"),
    # (AnalyzeType.KEYWORD, " T_"),
    # (AnalyzeType.KEYWORD, " T_0 "),
    # (AnalyzeType.KEYWORD, " T_0."),
    # (AnalyzeType.KEYWORD, " T_1."),
    # (AnalyzeType.KEYWORD, " T_2."),
    # (AnalyzeType.KEYWORD, " T_3."),
    #
    # (AnalyzeType.PATTERN_AVG, " B_(\\d+\\.?\\d*)"),
    # (AnalyzeType.PATTERN_AVG, " B_(-?\\d+\\.?\\d*)"),
    # (AnalyzeType.PATTERN_AVG, " B_(-\\d+\\.?\\d*)"),
    # (AnalyzeType.PATTERN_AVG, " T_(\\d+\\.?\\d*)"),
    # (AnalyzeType.PATTERN_AVG, " S_(\\d+\\.?\\d*)"),
    # (AnalyzeType.PATTERN_AVG, " P_(\\d+\\.?\\d*)"),
    # (AnalyzeType.PATTERN_AVG, " A_(-?\\d+\\.?\\d*)"),
    #
    # (AnalyzeType.KEYWORD, "Executing event: back"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __back"),
    # (AnalyzeType.PATTERN_AVG, "Function __back cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: home"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __home"),
    # (AnalyzeType.PATTERN_AVG, "Function __home cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: menu"),
    # (AnalyzeType.KEYWORD, "Executing event: rotate to nature"),
    # (AnalyzeType.KEYWORD, "Executing event: volume"),
    # (AnalyzeType.KEYWORD, "Executing event: scroll"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __scroll"),
    # (AnalyzeType.PATTERN_AVG, "Function __scroll cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: scroll up"),
    # (AnalyzeType.KEYWORD, "Executing event: scroll down"),
    # (AnalyzeType.KEYWORD, "Executing event: scroll left"),
    # (AnalyzeType.KEYWORD, "Executing event: scroll right"),
    # (AnalyzeType.KEYWORD, "Wrong direction"),
    # (AnalyzeType.KEYWORD, "Executing event: click by"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __click_by_coordinates"),
    # (AnalyzeType.PATTERN_AVG, "Function __click_by_coordinates cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: long_click by"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __long_click_by_coordinates"),
    # (AnalyzeType.PATTERN_AVG, "Function __long_click_by_coordinates cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: edit num with"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __edit_num"),
    # (AnalyzeType.PATTERN_AVG, "Function __edit_num cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: edit text with"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __edit_text"),
    # (AnalyzeType.PATTERN_AVG, "Function __edit_text cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "Executing event: edit all with"),
    # (AnalyzeType.PATTERN_AVG, "Event thread start, sleep (\\d+\\.?\\d*)s for __edit_all"),
    # (AnalyzeType.PATTERN_AVG, "Function __edit_all cost time: (\\d+\\.?\\d*)s"),
    # (AnalyzeType.KEYWORD, "!!! Event execution Failed !!!"),
    # (AnalyzeType.KEYWORD, "!!! Execution thread Failed !!!"),

    (AnalyzeType.PATTERN_AVG, "Function generate_jacoco_xml_report cost time: (\\d+\\.?\\d*)s"),
    (AnalyzeType.PATTERN_ONE, "Function generate_jacoco_coverage_final_result cost time: (\\d+\\.?\\d*)s")
]

ANALYZE_LIST = ANALYZE_LIST[:1]
COVERAGE_ANALYZE_PATTERN = ANALYZE_LIST[:1]


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


# if __name__ == '__main__':
#     analyze_all_apps(
#         tag_list=[
#             "DQT-0721-new_dqn-1",
#             "DQT-0721-new_dqn-2",
#             "DQT-0721-new_dqn-3",
#         ],
#         only_coverage=True,
#     )
