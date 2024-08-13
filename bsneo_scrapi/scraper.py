from pathlib import Path
from typing import Callable

from .paths import check_base_path
from .platform import Platform

#
# Scraper
# Base Class for all scrapers
#

class Scraper():
	# Page request timeout
	FETCH_TIMEOUT = 15

	# Path objects of games to scrape
	files: list[Path] = []

	# Platform for which games belong to.
	platform: Platform = None

	# Toggle for whether or not to rescrape existing entries
	rescrape_existing: bool = False

	# Output stream function
	output: Callable[..., None] = None

	# Status update function
	send_status: Callable[dict, None] = None

	# Assign values
	def __init__(self, files: list[Path], platform: Platform, rescrape_existing: bool, send_status: Callable[dict, None], output: Callable[..., None]) -> None:
		self.platform = platform
		self.rescrape_existing = rescrape_existing

		self.files = files

		self.send_status = send_status
		self.output = output

		# Check if base path exists. Other path checks will occur at their respective stages.
		check_base_path()

	# SKELETON METHOD:
	# Get the page with the game's metadata
	# return: A string with the contents of the page.
	#   If the request failed, return (False, "")
	def get_data_page(self, link: str) -> str:
		return ""

	# SKELETON METHOD:
	# Get the metadata for a single game from its metadata page.
	# return: A dictionary with the game's metadata.
	def get_metadata(self, filepath: Path, content: str) -> dict:
		return {}

	# SKELETON METHOD:
	# Scrape one or more games via the scraper class's service
	# return: A dictionary with the game(s)' metadata.
	#   The dictionary is required to have two fields:
	#   1. "entries": A list of textual metadata that mostly complies with format.md.
	#      Different Items:
	#      "imgs": imgs is a dict mapping asset types to lists of pairs of items.
	#      The first item a URL to the image, while the second item is the item's region.
	#      "video": video is an external URL to the video, not a filepath to a local file.
	#   2. "scraped_with": A short string representing the scraper service used for the entries.
	def scrape(self) -> dict:
		return {}
