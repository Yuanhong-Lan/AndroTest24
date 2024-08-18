# ----------------------
# @Time  : 2022 Apr
# @Author: Yuanhong Lan
# ----------------------
import os
from typing import NamedTuple, Dict, List, Union
from enum import Enum
from constant.platform_constant import PlatformConstant


class CoverageDetail(NamedTuple):
    covered: float
    total: float
    rate: float


class CoverageDetailWithStd(NamedTuple):
    covered: float
    total: float
    rate: float
    std: float
    std_lower: float
    std_upper: float


class CoverageItem(NamedTuple):
    time: int
    detail: Union[CoverageDetail, CoverageDetailWithStd]


class ECfileInfo(NamedTuple):
    relative_time: int
    raw_time: str
    source: str
    raw_file_name: str


class JavaVersion(Enum):
    JAVA_8 = "JAVA_8"
    JAVA_11 = "JAVA_11"
    JAVA_17 = "JAVA_17"


class ApkBriefInfo(NamedTuple):
    apk_file_name: str
    activity_count: int
    instruction_count: int


class ApkSourceCodeArgs:
    def __init__(self, apk_package: str, apk_root_relative_path: str, build_relative_path: str, java_version: JavaVersion):
        self._apk_package: str = apk_package
        self._root_path: str = os.path.join(PlatformConstant.INSTRUMENTED_CODE_ROOT, apk_root_relative_path)
        self._build_relative_path: str = build_relative_path
        self._java_version: JavaVersion = java_version

    @property
    def apk_package(self) -> str:
        return self._apk_package

    @property
    def root_path(self) -> str:
        return self._root_path

    @property
    def build_relative_path(self) -> str:
        return self._build_relative_path

    @property
    def java_version(self) -> JavaVersion:
        return self._java_version

    def get_raw_ec_dir(self, tag) -> str:
        return os.path.join(PlatformConstant.LOCAL_EC_DIR, tag, self.apk_package)


def get_readable_final_coverage_info_string(data: Dict[str, List[CoverageItem]]):
    res = []
    for key, value in data.items():
        max_time_length = len(str(value[-1].time))
        res.append(key)
        for item in value:
            res.append(f"    {item.time:>{max_time_length}}    {item.detail}")
    return '\n'.join(res)
