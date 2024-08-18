import re
from typing import Dict

import pandas as pd


class PatternUtil:
    @staticmethod
    def is_pattern_valid(pattern):
        assert (pattern.endswith('*')) or (pattern.endswith('~')) or (
                '**' in pattern), f"Pattern [{pattern}] is not valid."

    @staticmethod
    def is_match(pattern, s):
        PatternUtil.is_pattern_valid(pattern)

        if pattern == s:
            return True
        elif pattern.endswith('*'):
            # A* matches A-1, A-2, A-3, ...
            re_exp = f"{pattern[:-1]}-\\d+$"
            return re.match(re_exp, s)
        elif pattern.endswith('~'):
            # A~ means start with A
            return s.startswith(pattern[:-1])
        elif '**' in pattern:
            # A**-B matches A-1-B, A-2-B, A-3-B, ...
            re_exp = pattern.replace('**', "-\\d+")
            return re.match(re_exp, s)
        return False

    @staticmethod
    def is_match_among_list(pattern_list, s):
        for pattern in pattern_list:
            if PatternUtil.is_match(pattern, s):
                return True
        return False

    @classmethod
    def rename_dataframe_by_tag_pattern_dict(cls, df: pd.DataFrame, tag_pattern_dict: Dict[str, str]) -> None:
        rename_dict = {}
        for item in df.index:
            for pattern, target in tag_pattern_dict.items():
                if cls.is_match(pattern, item):
                    rename_dict[item] = target
                    break
        df.rename(index=rename_dict, inplace=True)
