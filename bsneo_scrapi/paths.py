from pathlib import Path
from platformdirs import (
	user_data_dir,
	user_config_dir
)

#
# paths
# List of directories to common paths
#

# Constants

APP_NAME = "bsneo"
APP_AUTHOR = "pquirrel"

# Paths

PATH_BASE = Path(user_data_dir(APP_NAME, APP_AUTHOR))
PATH_CONFIG = Path(user_config_dir(APP_NAME, APP_AUTHOR)).joinpath("config.json")

def PATH_SYS(pid: str):
	return PATH_BASE.joinpath(pid + "/")

def PATH_MEDIA(pid: str):
	return PATH_SYS(pid).joinpath("media/")

def PATH_META(pid: str):
	return PATH_SYS(pid).joinpath("metadata/")

# Check if base directory exists, create if it doesn't
def check_base_path():
	if not(PATH_BASE.exists()):
		PATH_BASE.mkdir()

# Check if the config file's directory exists, create if it doesn't
def check_config_path():
	CFG_DIR = PATH_CONFIG.parent
	if not(CFG_DIR.exists()):
		CFG_DIR.mkdir()

# Check if directory exists, create if it doens't
def check_path(path: Path):
	if not(path.exists()):
		path.mkdir(parents = True)
