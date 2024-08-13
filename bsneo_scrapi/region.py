from pathlib import Path

#
# region
# Various functions and constants relating to regions.
#

REGIONS = [
	"none", # No Region Specified
	"world", # World
	"na", # North America
	"eu", # Europe
	"jp", # Japan
	"us", # United States
	"ca", # Canada
	"uk", # United Kingdom
	"au", # Australia
	"nz", # New Zealand
	"es", # Spain
	"fr", # France
	"it", # Italy
	"de", # Germany
	"nl", # The Netherlands
	"ru", # Russia
	"kr", # Korea
	"hk", # Hong Kong
	"cn", # China
]

# Extracts the region code from the given path.
# return: the region code at the end of the path's basename.
def region_from_path(path: Path) -> str:
	basename: str = path.stem.split(".")[0]
	return basename[basename.rindex("_") + 1:]

# Gets a list of preferred regions from the given region code, ordered by priority.
# A preferred region is a region which encompasses a given region or which is similar,
# e.g. "us" has preferred regions "na" and "world".
# The first region will always be region_code, and the last two regions will always be "world" and "none".
#   Note For Developers: It is recommended, but not required, to have the
#   preferred region be either as specific as possible or for no region to be specified.
# return: A list of preferred regions. If region code is blank, return all regions.
def get_preferred_regions(region_code: str) -> list[str]:
	# Base preferences
	prefs = [region_code, "world", "none"]

	# No preference
	if region_code == "none":
		prefs = ["world", "none"]
		for region in regions[2:]:
			prefs.append(region)

	# North America
	if region_code in ("us", "ca"):
		prefs.insert(1, "na")

	# Europe
	if region_code in ("uk", "es", "fr", "it", "de", "nl", "ru"):
		prefs.insert(1, "eu")

	return prefs

