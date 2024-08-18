# ----------------------
# @Time  : 2023 Aug
# @Author: Yuanhong Lan
# ----------------------
import os
import yaml

from android_testing_utils.log import my_logger
from constant.platform_constant import PlatformConstant


config_file_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
config_data = yaml.safe_load(open(config_file_path))
my_logger.hint(
    my_logger.LogLevel.INFO, "Constant", True,
    f"Loading configs for Constant from {config_file_path}"
)


def log_module_configs(target_module):
    for target in [key for key, value in target_module.__dict__.items() if not key.startswith('_')]:
        exec(f"{target_module.__name__}.{target} = config_data['{target_module.__name__}']['{target}']")
    for key, value in target_module.__dict__.items():
        if not key.startswith('_'):
            assert (value is not None) and (value != ""), f"Please check the config file. {key} is not set."

    my_logger.hint(my_logger.LogLevel.INFO, "Constant", False, f"Current {target_module.__name__}:")
    for key, value in target_module.__dict__.items():
        if not key.startswith('_'):
            my_logger.hint(my_logger.LogLevel.INFO, "Constant", False, f"    {key}: {value}")


modules = [PlatformConstant]
for module in modules:
    log_module_configs(module)
