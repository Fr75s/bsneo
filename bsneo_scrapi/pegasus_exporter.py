from pathlib import Path
from typing import Callable

import re, json

from .paths import *
from .region import *
from .exporter import Exporter
from .platform import Platform
from .formatting import str_to_clean

#
# PegasusExporter
# Exporter class for exporting to metadata.pegasus.txt format.
# https://pegasus-frontend.org/
#

# Constants
# List of metadata.pegasus.txt fields which treat multi-line data as lists rather than
# paragraphs of text.
# These are prefixes i.e. if the field starts with a string in this list, it is list-type data.
LIST_TYPE_FIELD_PREFIXES = [
	"extension",
	"file",
	"director", # directory / directories
	"developer",
	"publisher",
	"genre",
	"tag"
]

# Convert list type field prefixes to their plural variants
# Note that this will also attempt to replace *List with *s for any non-asset resource.
FIELD_PREFIX_TO_PLURAL = {
	"extension": "extensions",
	"director": "directories",
	"developer": "developers",
	"publisher": "publishers",
	"genre": "genres",
	"tag": "tags",
	"developerList": "developers",
	"publisherList": "publishers",
	"genreList": "genres",
	"tagList": "tags"
}

# Renamed fields from bsneo JSON
BSNEO_JSON_RENAME = {
	"name": "game",
	"desc": "description",
	"filename": "file"
}

# Order for which to put new data.
PEGASUS_DATA_ORDER = [
	"game",
	"file",
	"description",
	"release",
	"developers",
	"publishers",
	"genres",
	"players",
]

class PegasusExporter(Exporter):
	# Initialize Base Exporter
	def __init__(self, platform: Platform, base_region: str, strict_region: bool, send_status: Callable[dict, None], output: Callable[..., None]) -> None:
		super().__init__(platform, base_region, strict_region, send_status, output)

	# Determines whether or not the given field is list type via LIST_TYPE_FIELD_PREFIXES.
	def is_list_type_field(self, field: str) -> bool:
		for prefix in LIST_TYPE_FIELD_PREFIXES:
			if prefix in field:
				return True
		return False

	# Helper method for read_existing_metadata.
	# Adds the given data to the given field in data_section.
	def add_data_to_field(self, data_section: dict, field: str, data: str) -> None:
		# Check if this is a list type field
		list_type_field = self.is_list_type_field(field)

		# Check if field is already present
		if field in data_section:
			# Append data to field
			if list_type_field:
				data_section[field].append(data)
			else:
				data_section[field] += data
		else:
			if list_type_field:
				if data == "":
					data_section[field] = []
				else:
					data_section[field] = [data]
			else:
				data_section[field] = data

	# Reads an existing metadata.pegasus.txt file.
	# If this file is nonexistent, return None.
	# return: A list of data blocks, each holding metadata for one game.
	#   The first data block holds metadata for the collection.
	def read_existing_metadata(self, existing_file: Path) -> list[dict]:
		# Check if file exists
		if not (existing_file.exists()):
			return None

		self.output("Getting existing metadata...", 0)

		# Read metadata file
		metadata_lines = []
		with open(existing_file, "r") as metadata_file:
			# Get lines
			metadata_lines_raw = metadata_file.readlines()

			# Split file by blank lines
			i = 0
			current_field = ""
			# NL: "New Line", consolidates consecutive blank lines to act as only one
			nl = False
			for line in metadata_lines_raw:
				if line.strip(" ") == "\n":
					# Check if this is a consecutive newline
					if not nl:
						# Queue creation of new data block
						i += 1
						current_field = ""
						nl = True
				elif line[0] != "#":
					# This line is not a comment nor a blank line, therefore
					# create a new data section
					nl = False
					if len(metadata_lines) == i:
						metadata_lines.append({})

					# Check if line contains field definition
					contains_definition = re.match(r"\s", line) == None
					if contains_definition:
						# This line contains a field definition.
						# Extract the field of this line. Throw an error if the field doesn't exist.
						field = line[:line.index(":")].strip(" ")
						# Extract the data of this line.
						data = line[line.index(":") + 1:-1].strip(" ")

						# Add the data to metadata_lines.
						self.add_data_to_field(metadata_lines[i], field, data)
						current_field = field
					else:
						# This line is a continuation of the data from the previous line.
						new_data = line.strip(" ")[:-1]
						if new_data == ".":
							self.add_data_to_field(metadata_lines[i], current_field, "\n\n")
						else:
							self.add_data_to_field(metadata_lines[i], current_field, new_data)

		self.output(f"{metadata_lines}", -1)
		return metadata_lines

	# Deletes any non-plural list-type fields from existing_entry, as listed in FIELD_PREFIX_TO_PLURAL.
	# If any data was present in the non-plural field, move it to the plural equivalent.
	def delete_non_plural_fields(self, existing_entry: dict) -> None:
		fields_queued_for_deletion = []
		for field_pfx in LIST_TYPE_FIELD_PREFIXES:
			# Ignore file
			if field_pfx != "file":
				for field_name in existing_entry:
					# Check if non-plural field name is in existing_entry
					if field_pfx in field_name and not field_name in [*FIELD_PREFIX_TO_PLURAL.values()]:
						# Non-plural list type found
						field_plural = FIELD_PREFIX_TO_PLURAL[field_pfx]
						# Add any items here to plural list type if not already present
						for item in existing_entry[field_name]:
							if not item in existing_entry[field_plural]:
								existing_entry[field_plural].append(item)
						# Queue non-plural field for deletion
						fields_queued_for_deletion.append(field_name)

		# Delete fields queued prior
		for field in fields_queued_for_deletion:
			del existing_entry[field]

	# Converts bsneo JSON metadata to a Pegasus metadata block.
	# meta_json: The JSON data as read from the metadata file.
	# media_copied: A dictionary mapping asset types to the media located in
	# the destination folder. This can be acquired from copy_media.
	def json_to_block(self, meta_json: dict, media_copied: dict) -> dict:
		self.output(f"Converting data for {meta_json['name']} to block format", -1)

		# Remove Fields
		for field in ("platform", "clean_name", "imgs"):
			del meta_json[field]

		# Rename Fields
		for field in BSNEO_JSON_RENAME:
			if field in meta_json:
				meta_json[BSNEO_JSON_RENAME[field]] = meta_json[field]
				del meta_json[field]

		# Change file to list
		meta_json["file"] = [meta_json["file"]]

		# Rearrange Fields
		meta_block = {}
		for field in PEGASUS_DATA_ORDER:
			if field in meta_json:
				meta_block[field] = meta_json[field]

		# Change imgs[*] to assets.*
		for asset_type in media_copied:
			if asset_type != "box3d":
				asset_path = str(media_copied[asset_type])
				asset_path = asset_path[asset_path.index("media/"):]

				meta_block[f"assets.{asset_type}"] = asset_path

		return meta_block

	# Converts a series of metadata blocks to metadata.pegasus.txt format.
	# return: The output in metadata.pegasus.txt format as a list of lines
	def blocks_to_file(self, blocks: list[dict]) -> list[str]:
		out = []

		# Sort blocks by "game" field, keeping the collection block first.
		sorted_blocks = sorted(blocks[1:], key=lambda block: block["game"])
		sorted_blocks.insert(0, blocks[0])

		# Convert blocks
		for entry in sorted_blocks:
			# Empty line above
			out.append(f"\n")
			# Add data
			for field in entry:
				if self.is_list_type_field(field):
					# Add all items of list type fields in format
					# field:
					#  item 1
					#  item 2
					#  ...
					out.append(f"{field}:\n")
					for item in entry[field]:
						out.append(f"  {item}\n")
				else:
					# Add all lines of text type format
					# Split data by lines
					split_value = entry[field].split("\n")
					# Convert paragraph breaks into periods
					for i in range(len(split_value)):
						if split_value[i] == "":
							split_value[i] = "."
					# Add to output
					out.append(f"{field}: {split_value[0]}\n")
					for line in split_value[1:]:
						out.append(f"  {line}\n")

		# Remove first empty line
		return out[1:]


	# Export Games to metadata.pegasus.txt format
	def export_system(self, dest: Path) -> list[str]:
		# Check if dest is a directory that exists
		if dest.is_dir():
			self.output("Destination path is a directory!", 1)
			return []

		exported = []

		# Get existing data
		existing_meta: list[dict] = self.read_existing_metadata(dest)
		if existing_meta == None:
			# No existing data
			self.output("No existing data found.", 0)

			meta_blocks = []
			game_names = []
			for meta_file in PATH_META(self.platform.pid).iterdir():
				# Record that this game is in the metadata file
				game_names.append(str_to_clean(meta_file.name[:-5]))
				# Copy over media for this game to destination folder
				copied_media = self.copy_media(meta_file, dest.parent)
				with open(meta_file, "r") as meta_file_content:
					# Read metadata file and convert to block
					metadata = json.loads(meta_file_content.read())
					meta_blocks.append(self.json_to_block(metadata, copied_media))

			# Create collection data block and insert
			collection_block = {
				"collection": self.platform.fullname,
				"shortname": self.platform.pid,
				"launch": "\"Insert Launch Command Here!\""
			}
			meta_blocks.insert(0, collection_block)

			# Convert to correct format and write output
			self.output("Writing data to file...", 0)
			output_lines = self.blocks_to_file(meta_blocks)
			with open(dest, "w") as dest_file:
				dest_file.writelines(output_lines)

			return game_names
		else:
			# There is existing data
			# Check if existing data is for the same system
			if existing_meta[0]["shortname"] == self.platform.pid:
				self.output("Existing Data Found! Integrating any new data...", 0)

				# Existing data is for the same system
				# Get cleaned names of existing games
				existing_game_names = []
				for game_entry in existing_meta[1:]:
					existing_game_names.append(str_to_clean(game_entry["game"]))

				self.output(f"Existing: {existing_game_names}", -1)

				# Add any non-preexisting games
				for meta_file in PATH_META(self.platform.pid).iterdir():
					# Check if this game is already in the metadata file.
					clean_game_name: str = str_to_clean(meta_file.name[:-5])
					self.output(f"Checking if {clean_game_name} is already present...", -1)

					# Overwrite any already present media & copy any new media
					copied_media = self.copy_media(meta_file, dest.parent)
					with open(meta_file, "r") as meta_file_content:
						# Get metadata
						metadata = json.loads(meta_file_content.read())
						metadata_block = self.json_to_block(metadata, copied_media)

						if clean_game_name in existing_game_names:
							# This game is already in the metadata file.
							self.output(f"Already present, substituting fields...", -1)
							existing_entry_idx: int = existing_game_names.index(clean_game_name) + 1

							# Replace fields
							for field in metadata_block:
								existing_meta[existing_entry_idx][field] = metadata_block[field]

							# Delete non-plural fields
							self.delete_non_plural_fields(existing_meta[existing_entry_idx])
						else:
							# This game is not in the metadata file.
							self.output(f"Not present, adding...", -1)
							existing_meta.append(metadata_block)
							existing_game_names.append(clean_game_name)

				# Convert to correct format and write output
				self.output("Writing data to file...", 0)
				output_lines = self.blocks_to_file(existing_meta)
				with open(dest, "w") as dest_file:
					dest_file.writelines(output_lines)

				return existing_game_names
			else:
				self.output("Destination file holds metadata for a different system.", 1)
				return []
