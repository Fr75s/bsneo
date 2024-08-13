from pathlib import Path
from typing import Callable

import json, shutil

from .paths import *
from .region import *
from .platform import Platform

#
# Exporter
# Base Class for all exporters
#

class Exporter():
	# Platform for which games belong to.
	platform: Platform = None

	# Base Preferred Region.
	base_region: str = "none"

	# Strict Region Match Mode:
	# If True, images outside of region prefs are not considered. Some asset types which
	# were downloaded may be missing as a result.
	strict_region: bool = False

	# Output stream function
	output: Callable[..., None] = None

	# Status update function
	send_status: Callable[dict, None] = None

	# Assign values
	def __init__(self, platform: Platform, base_region: str, strict_region: bool, send_status: Callable[dict, None], output: Callable[..., None]) -> None:
		# Init Exporter Settings
		self.platform = platform
		self.base_region = base_region
		self.strict_region = strict_region

		# Status and Output functions for worker class
		self.send_status = send_status
		self.output = output

	# Copies over all media files for a single game given the game's name and a media identifier.
	# By default, the file is copied over with the same name, excluding the region code.
	# rename can be used to rename the copied file.
	# meta_file: The bsneo metadata JSON for this game
	# dest: The destination media folder. Files will be copied into {dest}/media/{game}/
	# rename: A dictionary with media identifiers as keys and new names as values. The file's
	#   media identifier will be changed to rename[media] on copy.
	#   Blank by default, which results in no renaming.
	# return: A dictionary that maps asset types to copied files.
	def copy_media(self, meta_file: Path, dest: Path, rename: dict[str, str] = {}) -> dict[str, Path]:
		# Get source images list
		imgs = {}
		game = ""
		with open(meta_file, "r") as meta_content:
			metadata = json.loads(meta_content.read())
			imgs = metadata["imgs"]
			game = metadata["clean_name"]

		# Get copy destination
		final_dest: Path = dest.joinpath("media", game)
		check_path(final_dest)

		# Determine images to copy by region
		to_copy: dict[str, Path] = {}
		# Get preferred regions
		pref_reg = get_preferred_regions(self.base_region)
		for asset_type in imgs:
			# Find image for this asset type with highest region priority
			highest_pref_idx = len(REGIONS)
			highest_pref_img = -1
			for i in range(len(imgs[asset_type])):
				# Get image file as Path object
				img_path = Path(imgs[asset_type][i])
				# Get region of this image
				region = region_from_path(img_path)

				# Check if in preferred region or if it doesn't matter
				if region in pref_reg:
					highest_pref_idx = pref_reg.index(region)
					highest_pref_img = i
				elif not self.strict_region and highest_pref_idx == len(REGIONS):
					highest_pref_img = i
			if highest_pref_img >= 0:
				# Add to images to copy
				to_copy[asset_type] = Path(imgs[asset_type][highest_pref_img])

		# Copy over images
		for asset_type in to_copy:
			# Get file to write to (renaming if necessary)
			file_dest = None
			new_filename = to_copy[asset_type].name
			# Remove region code
			new_filename = new_filename[:new_filename.rindex("_")] + new_filename[new_filename.rindex("."):]
			# Rename if necessary
			if asset_type in rename:
				new_filename = new_filename.replace(asset_type, rename[asset_type])

			file_dest = final_dest.joinpath(new_filename)

			shutil.copy(to_copy[asset_type], file_dest)
			to_copy[asset_type] = file_dest

		return to_copy

	# SKELETON METHOD:
	# Gets the metadata from an existing file with the exporter class's file format.
	# existing_file: The existing metadata file.
	# return: A list consisting of the metadata for each game.
	def read_existing_metadata(self, existing_file: Path) -> list[dict]:
		return []

	# SKELETON METHOD:
	# Export all of the games from this Exporter's platform to the exporter class's file format.
	# If there is already an exported file at dest, update that file with any newly scraped entries.
	# dest: The destination directory for which the exported file and all media will be placed.
	# return: A list of all entries in the outputted file.
	#   If any errors occurred, return a blank list.
	def export_system(self, dest: Path) -> list[str]:
		return []
