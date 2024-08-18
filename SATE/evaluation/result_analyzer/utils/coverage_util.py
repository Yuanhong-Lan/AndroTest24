from typing import List, Dict, Optional

from runtime_collection.collector_util.util_coverage import CoverageItem, CoverageDetail, CoverageDetailWithStd


class CoverageTimeUtil:
    @staticmethod
    def padding_data(raw_data: List[CoverageItem], full_time_list: List[int], need_std=False) -> List[CoverageItem]:
        # set(raw_time_list) ⊆ set(full_time_list)
        raw_time_list: List[int] = [i.time for i in raw_data]

        res = []
        if not need_std:
            current_data = CoverageDetail(0, raw_data[0].detail.total, 0)
        else:
            current_data = CoverageDetailWithStd(0, raw_data[0].detail.total, 0, 0, 0, 0)
        for relative_time in full_time_list:
            if relative_time in raw_time_list:
                current_data = raw_data[raw_time_list.index(relative_time)].detail
            res.append(CoverageItem(relative_time, current_data))
        return res

    @staticmethod
    def normalize_time_for_data_list(raw_data: List[CoverageItem], normalize_time: int) -> List[CoverageItem]:
        rate = normalize_time / raw_data[-1].time
        res = []
        for item in raw_data:
            res.append(
                CoverageItem(int(item.time * rate), item.detail)
            )
        return res

    @staticmethod
    def normalize_time_for_data_dict(raw_data: Dict[str, List[CoverageItem]], normalize_time: int) -> Dict[str, List[CoverageItem]]:
        res = {}
        for key, value in raw_data.items():
            res[key] = CoverageTimeUtil.normalize_time_for_data_list(value, normalize_time)
        return res

    @staticmethod
    def get_appointed_time_coverage(
            raw_data: List[CoverageItem],
            target_time: Optional[int] = None,
            normalize_time: Optional[int] = None,
    ) -> float:
        if (normalize_time is not None) and (raw_data[-1].time > normalize_time):
            raw_data = CoverageTimeUtil.normalize_time_for_data_list(raw_data, normalize_time)

        if (target_time is None) or (target_time == normalize_time):
            return raw_data[-1].detail.rate * 100

        raw_data = CoverageDataUtil.extend_coverage_data_list_with_standard_time_series(
            raw_data, target_time, target_time,
        )

        target_rate = None
        for item in raw_data:
            if item.time <= target_time:
                target_rate = item.detail.rate
            if item.time > target_time:
                break

        return target_rate * 100


class CoverageDataUtil:
    @staticmethod
    def extend_coverage_data_list_with_standard_time_series(
            raw_data_list: List[CoverageItem],
            length: int,
            interval: int,
            need_std=False,
    ) -> List[CoverageItem]:
        raw_time_list: List[int] = [i.time for i in raw_data_list]
        temp_time_list: List[int] = [i * interval for i in range(int(length / interval + 1))]
        full_time_list = sorted(list(set(temp_time_list + raw_time_list)))

        res = CoverageTimeUtil.padding_data(raw_data_list, full_time_list, need_std)
        return res

    @staticmethod
    def extend_coverage_data_dict_with_standard_time_series(
            raw_data_dict: Dict[str, List[CoverageItem]],
            length: int,
            interval: int,
            need_std=False,
    ) -> Dict[str, List[CoverageItem]]:
        res = {}
        for key, value in raw_data_dict.items():
            res[key] = CoverageDataUtil.extend_coverage_data_list_with_standard_time_series(value, length, interval, need_std)
        return res

    @staticmethod
    def __filter_coverage_data_list_with_standard_time_series(
            raw_data_list: List[CoverageItem],
            length: int,
            interval: int,
    ) -> List[CoverageItem]:
        res = []
        temp_time_list: List[int] = [i * interval for i in range(int(length / interval + 1))]
        for item in raw_data_list:
            if item.time in temp_time_list:
                res.append(item)
        return res

    @staticmethod
    def filter_coverage_data_dict_with_standard_time_series(
            raw_data_dict: Dict[str, List[CoverageItem]],
            length: int,
            interval: int,
    ) -> Dict[str, List[CoverageItem]]:
        res = {}
        for key, value in raw_data_dict.items():
            res[key] = CoverageDataUtil.__filter_coverage_data_list_with_standard_time_series(value, length, interval)
        return res
