from pathlib import Path
from typing import Callable
import threading

from .region import REGIONS
from .platform import *

# Scrapers
from .scraper import Scraper
from .lbscraper import LBScraper

# Info Compiler
from .info_compiler import InfoCompiler

# Exporters
from .exporter import Exporter
from .pegasus_exporter import PegasusExporter

#
# Worker
# Main Interface for bsneo-scrapi
# Wrapper for all scraping steps and enables multithreading.
#

# Exception class to raise when scraper or exporter is undefined on run/export
class UndefinedTaskRunnerError(Exception):
	pass

class Worker():
	# Files that will be scraped by the scraper
	files: list[Path] = []

	# Export Destination
	export_dest: Path = None

	# Platform for the scraper/exporter
	platform: Platform = None

	# The scraper class instance for this worker.
	scraper: Scraper = None

	# The exporter class instance for this worker.
	exporter: Exporter = None

	# Initialize output wrapper for output to be sent over to the main application.
	def __init__(self, output_wrapper: Callable[..., None], on_status_change: Callable[..., None]=lambda *args: None) -> None:
		self.output_wrapper = output_wrapper
		self.on_status_change = on_status_change

		# Settings used by the scraper or the exporter
		self.settings: dict = {}

		# Current Status
		self.status: dict = {}

	# Set or override options that the scraper or exporter can use.
	def set_worker_settings(self, opts: dict) -> None:
		for opt in opts:
			self.settings[opt] = opts[opt]

	# Set the files that the worker should scrape.
	def set_worker_files(self, files: list[Path]) -> None:
		self.files = files

	# Set the destination file for exporting.
	def set_worker_export_dest(self, dest: Path) -> None:
		self.export_dest = dest

	# Set the platform via the platform's ID. If not present, do not set.
	# return: True if the platform was set, False otherwise
	def set_platform(self, pid: str) -> bool:
		if pid in PLATFORMS:
			self.platform = PLATFORMS[pid]
			return True
		return False

	# Initialize the scraper class with the given settings.
	# return: A blank list if the scraper was initialized, otherwise a list of values that
	#   need to be specified for the scraper to work.
	def set_scraper(self, scraper_id: str) -> list[str]:
		# Check for missing generic scraper settings
		invalid_settings = []
		# Missing Platform
		if self.platform == None:
			invalid_settings.append("platform")
		# Missing Output Function
		if self.output_wrapper == None:
			invalid_settings.append("output")
		# Missing Rescrape Existing Setting
		if not "rescrape_existing" in self.settings or type(self.settings["rescrape_existing"]) != bool:
			invalid_settings.append("rescrape_existing")

		if len(invalid_settings) > 0:
			return invalid_settings

		# Scraper Specifics
		match scraper_id:
			case "lb":
				# LaunchBox
				# Missing Files
				if not type(self.files) == list or len(self.files) == 0:
					return ["files"]

				# Set Scraper
				self.scraper = LBScraper(self.files, self.platform, self.settings["rescrape_existing"], self.update_status, self.output_wrapper)
			case _:
				return ["scraper_id"]

		return []

	# Initialize the exporter class with the given settings.
	# return: A blank list if the exporter was initialized, otherwise a list of values that
	#   need to be specified for the exporter to work.
	def set_exporter(self, exporter_id: str) -> list[str]:
		# Check for missing generic exporter settings
		invalid_settings = []
		# Missing Platform
		if self.platform == None:
			invalid_settings.append("platform")
		# Missing Output Function
		if self.output_wrapper == None:
			invalid_settings.append("output")
		# Missing Preferred Region
		if not ("region" in self.settings and self.settings["region"] in REGIONS):
			invalid_settings.append("region")
		# Missing Strict Region Mode
		if not ("strict_region" in self.settings and type(self.settings["strict_region"]) == bool):
			invalid_settings.append("strict_region")
		# Missing Export Destination
		if not isinstance(self.export_dest, Path):
			invalid_settings.append("destination")

		if len(invalid_settings) > 0:
			return invalid_settings

		# Scraper Specifics
		match exporter_id:
			case "pf":
				# Set Exporter
				self.exporter = PegasusExporter(self.platform, self.settings["region"], self.settings["strict_region"], self.update_status, self.output_wrapper)
			case _:
				return ["exporter_id"]

		return []

	# Sends a new status to the class using this worker.
	def update_status(self, status: dict) -> None:
		for key in status:
			self.status[key] = status[key]
		self.on_status_change(self.status)

	# Scrape the specified games and save the data.
	def run(self) -> None:
		# Check if Scraper was initialized
		if self.scraper == None:
			raise UndefinedTaskRunnerError(
				"Please specify a scraper before attempting to run a scrape task."
			)

		# Scrape
		scraped_data: dict = self.scraper.scrape()

		# Check if an error occurred while scraping
		if not scraped_data["error"]:
			# No Error Occurred, continue as normal.
			# Initialize InfoCompiler
			download_video = False
			if "video_dl" in self.settings and type(self.settings["video_dl"]) == bool:
				download_video = self.settings["video_dl"]

			info_compiler: InfoCompiler = InfoCompiler(self.platform, download_video, self.update_status, self.output_wrapper)

			# Compile Information
			info_compiler.process(scraped_data)
			self.update_status({"code": "finished", "details": "Nothing Left to Do"})

	# Export saved metadata.
	def export(self) -> None:
		# Check if Exporter was initialized
		if self.exporter == None:
			raise UndefinedTaskRunnerError(
				"Please specify an exporter before attempting to run an export task."
			)

		# Export to export_dest
		games_exported: list[str] = self.exporter.export_system(self.export_dest)
		self.output_wrapper(f"Exported Games: {games_exported}.", 0)
		self.update_status({"code": "finished", "details": "Nothing Left to Do"})




