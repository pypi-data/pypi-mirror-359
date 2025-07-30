from keplemon._keplemon.time import load_time_constants  # type: ignore
from keplemon._keplemon import (  # type: ignore
    get_thread_count,
    set_thread_count,
    set_license_file_path,
    get_license_file_path,
)
from pathlib import Path
from shutil import copyfile

current_dir = Path(__file__).parent

# Copy the license file to the current working directory if it doesn't exist
LICENSE_PATH = current_dir / "SGP4_Open_License.txt"
local_path = Path.cwd() / "SGP4_Open_License.txt"
if not local_path.exists():
    copyfile(LICENSE_PATH, local_path)
set_license_file_path(LICENSE_PATH.as_posix())

# Load the time constants from the assets directory
TIME_CONSTANTS_PATH = current_dir / "assets" / "time_constants.dat"
load_time_constants(TIME_CONSTANTS_PATH.as_posix())

__all__ = [
    "get_thread_count",
    "set_thread_count",
    "TIME_CONSTANTS_PATH",
    "set_license_file_path",
    "LICENSE_PATH",
    "get_license_file_path",
]
