# ----------------------
# @Time  : 2024 May
# @Author: Yuanhong Lan
# ----------------------
import os
from typing import Dict, List, Callable, Optional

import numpy as np
import pandas as pd

from evaluation.result_analyzer.utils.data_util import DataType, StatisticDataUtil
from evaluation.result_analyzer.utils.path_util import ExcelDirectoryPathGenerator


class Variation:
    @classmethod
    def __write_tool_statistic_data(
            cls,
            excel_writer: pd.ExcelWriter,
            original_data: pd.DataFrame,
            tool_data_dict: Dict[str, Dict[str, np.ndarray]],
            tools: List[str],
            data_name: str,
            data_func: Callable,
            print_avg_res: bool = False,
    ):
        res_data = pd.DataFrame(columns=original_data.columns, index=tools)
        type_recorder = {tool: {} for tool in tools}
        for column in original_data.columns:
            current_type = column.split('-')[1]
            for tool in tools:
                if np.any(tool_data_dict[tool][column] < 0):
                    res_data.loc[tool, column] = -1
                else:
                    current_cv = data_func(tool_data_dict[tool][column])
                    res_data.loc[tool, column] = current_cv
                    if current_type not in type_recorder[tool]:
                        type_recorder[tool][current_type] = []
                    type_recorder[tool][current_type].append(current_cv)

        column_temp = [item.split('-')[1] for item in original_data.columns]
        column_temp = column_temp[:column_temp.index(column_temp[0], 1)]

        avg_data = pd.DataFrame(columns=column_temp, index=tools)
        for tool in type_recorder.keys():
            for current_type in type_recorder[tool].keys():
                avg_data.loc[tool, current_type] = np.round(np.mean(type_recorder[tool][current_type]), 2)

        median_data = pd.DataFrame(columns=set([item.split('-')[1] for item in original_data.columns]), index=tools)
        for tool in type_recorder.keys():
            for current_type in type_recorder[tool].keys():
                median_data.loc[tool, current_type] = np.median(type_recorder[tool][current_type])

        avg_data.loc["avg"] = np.round(avg_data.mean(axis=0), 2)

        res_data.to_excel(excel_writer, sheet_name=f"{data_name}_raw")
        avg_data.to_excel(excel_writer, sheet_name=f"{data_name}_avg")
        median_data.to_excel(excel_writer, sheet_name=f"{data_name}_med")

        if print_avg_res:
            print(avg_data)

    @classmethod
    def original_data_to_cv_data(
            cls,
            original_data_path: str,
            tools: List[str],
            data_type: DataType,
            slicing: Optional[int] = None,
            postfix: Optional[str] = None,
    ):
        original_data = pd.read_excel(original_data_path, index_col=0, header=0)
        tool_data_dict: Dict[str, Dict[str, np.ndarray]] = {
            tool: StatisticDataUtil.full_data_to_tool_ndarrays(original_data, tool, slicing)
            for tool in tools
        }
        excel_writer = pd.ExcelWriter(os.path.join(
            ExcelDirectoryPathGenerator.get_cv_data_dir(),
            f"{data_type.value}{'' if postfix is None else '_' + postfix}.xlsx"
        ))

        cls.__write_tool_statistic_data(
            excel_writer=excel_writer,
            original_data=original_data,
            tool_data_dict=tool_data_dict,
            tools=tools,
            data_name="cv",
            data_func=StatisticDataUtil.get_coefficient_of_variation,
        )
        cls.__write_tool_statistic_data(
            excel_writer=excel_writer,
            original_data=original_data,
            tool_data_dict=tool_data_dict,
            tools=tools,
            data_name="var",
            data_func=lambda x: np.var(x, ddof=1),
        )

        excel_writer.save()

    @classmethod
    def combine_cv_avg_data(
            cls,
            file_prefix: str,
            slicing_list: List[int],
    ):
        res = {}
        for slicing in slicing_list:
            data = pd.read_excel(
                os.path.join(ExcelDirectoryPathGenerator.get_cv_data_dir(), f"{file_prefix}{slicing}.xlsx"),
                sheet_name=None, index_col=0, dtype=str
            )
            for sheet_name, sheet_data in data.items():
                if sheet_name.endswith("_avg"):
                    for index, row in sheet_data.iterrows():
                        new_sheet_name = f"{sheet_name}|{index}"
                        if new_sheet_name not in res:
                            res[new_sheet_name] = pd.DataFrame(columns=sheet_data.columns)
                        res[new_sheet_name].loc[slicing] = row
        excel_writer = pd.ExcelWriter(os.path.join(ExcelDirectoryPathGenerator.get_cv_data_dir(), f"{file_prefix}all.xlsx"))
        for sheet_name, sheet_data in res.items():
            sheet_data.to_excel(excel_writer, sheet_name=sheet_name)
        excel_writer.save()
