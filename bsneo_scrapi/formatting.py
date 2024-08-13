from pathlib import Path
from datetime import datetime
from unidecode import unidecode
import os, re

#
# formatting
# Formatting functions to convert game paths to comparable game names
#


# Converts a string to a clean, comparable format.
# string: The string to clean up.
# return: The cleaned up name.
def str_to_clean(string: str) -> str:
	# Convert to upper case
	string = string.upper()

	# Remove anything in parentheses
	string = re.sub(r"\(.*\)|\[.*\]|\{.*\}", "", string)

	# Normalize text to ASCII
	string = unidecode(string)

	# Strip spaces
	string = string.strip(" ")

	# Substitute charcters
	string = re.sub(r"- |\.|,|!|\?|'|\"|-|", "", string)
	string = re.sub(r"(: )| |:", "_", string)
	string = re.sub(r"&", "AND", string)

	return string


# Converts a Path object to a clean, comparable game name.
# path: The path to the game file.
# return: The cleaned up game name.
def path_to_clean(path: Path) -> str:
	# Get file basename (without any suffixes)
	stem: str = path.stem.split(".")[0]
	return str_to_clean(stem)


# Normalizes a date from %B %d, %Y to ISO format
# date: The date in %B %d, %Y format
# return: The date in ISO format
def date_to_iso(date: str) -> str:
	return datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")

