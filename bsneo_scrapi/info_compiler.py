from typing import Callable
from yt_dlp import YoutubeDL
from pathlib import Path

import re, json, requests

from .paths import *
from .platform import Platform

#
# InfoCompiler
# Compiles the given information into JSON format
#

# Constants
# Download timeout in seconds
MEDIA_NETWORK_TIMEOUT = 15

# Default Video Length Limit in seconds
VIDEO_LEN_LIMIT = 120

class InfoCompiler():
	# The platform for which the games processed in process() belong to
	platform: Platform = None

	# Whether or not to download videos on this step
	video_dl: bool = False

	# Checks whether or not the video was actually downloaded
	video_downloaded: bool = False

	# Output stream function
	output: Callable[..., None] = None

	# Status update function
	send_status: Callable[dict, None] = None

	# Put data into field
	def __init__(self, platform: Platform, video_dl_now: bool, send_status: Callable[dict, None], output: Callable[..., None]) -> None:
		self.platform = platform
		self.video_dl = video_dl_now

		self.send_status = send_status
		self.output = output

	# Directly downloads an image from the given link
	# link: The URL which links to the image to be downloaded.
	# asset_type: The asset type of the image, which becomes part of its filename.
	# region: The region code of the image.
	# game_name: The clean name of the game entry which has this image.
	# returns a Path object to the downloaded image if successful, None otherwise.
	def download_image(self, link: str, asset_type: str, region: str, game_name: str) -> Path:
		# Store Raw Image Data
		image_data = None

		# Extract file extension from link
		file_ext: str = re.search(r"(\.[^.]+)$", link).group(0).lower()

		# Get image file path
		image_path: Path = PATH_MEDIA(self.platform.pid).joinpath(game_name, asset_type + "_" + region + file_ext)

		# Check if image already exists
		if not image_path.exists():
			# Attempt to Download the image
			try:
				self.output(f"Downloading Image from URL: {link}", -1)
				image_data = requests.get(link, timeout = MEDIA_NETWORK_TIMEOUT)
			except Exception as e:
				self.output(f"Image Download Failed: {e}", 1)
				return None

			# Write Image to File
			try:
				self.output(f"Writing Image to File ({asset_type}_{region}{file_ext})", -1)
				# Write to MEDIA_PATH/{NAME}
				with open(image_path, "wb") as image_file:
					image_file.write(image_data.content)
			except Exception as e:
				self.output(f"Image Write Failed: {e}", 1)
				return None

			# Indicate Success
			self.output(f"Successfully Downloaded {link}", 0)
			return image_path
		else:
			# Indicate Success
			self.output(f"Image {asset_type}_{region}{file_ext} Already Exists", 0)
			return image_path

	# Checks the length of the video to prevent the user from downloading a video that's too large.
	def video_len_test(self, info):
		duration = info.get("duration")
		if duration and duration > VIDEO_LEN_LIMIT:
			self.send_status({"video_progress": -2})
			return "Video is too long"

	# Hooks to the currently downloading video to output.
	def video_progress_hook(self, dl):
		if dl["status"] == "downloading":
			# Get # Bytes Downloaded so far
			downloaded = dl["downloaded_bytes"]

			# Get total video size (if possible)
			total = None
			if ("total_bytes" in d):
				total = dl["total_bytes"]
			elif ("total_bytes_estimate" in d):
				total = dl["total_bytes_estimate"]

			if not(total == None):
				# Output Video Download Progress
				self.output(f"Downloading Video: {(downloaded / total) * 100}%", -1)
				self.send_status({"code": "video", "video_progress": (downloaded / total)})
			else:
				# Send Indeterminate Video Download Progress
				self.send_status({"code": "video", "video_progress": -1})
		if dl["status"] == "finished":
			# Output that the video has finished downloading
			self.output("Video download has finished.", 0)
			self.send_status({"code": "video", "video_progress": 1.0})
			self.video_downloaded = True


	# Downloads the video from the given link. The link may be a direct video link or
	# a link to an external service.
	# link: The URL which links to the video to be downloaded.
	# game_name: The clean name of the game entry which has this image.
	# returns a Path object to the downloaded video if successful, None otherwise.
	def download_video(self, link: str, game_name: str) -> Path:
		# Define place to download video
		video_path = PATH_MEDIA(self.platform.pid).joinpath(game_name, "video.mp4")

		# Define filter for capping video length, progress hook
		# for capturing download progress, and output file.
		dl_options = {
			"match_filter": self.video_len_test,
			"outtmpl": str(video_path),
			"progress_hooks": [self.video_progress_hook]
		}

		# Download Video via yt-dlp
		self.send_status({"code": "video", "video_progress": 0.0})
		with YoutubeDL(dl_options) as video_downloader:
			err = video_downloader.download(link)
			if err == 0:
				return video_path

		return None

	# Processes all "entries" entries in the given metadata dict, and downloads images.
	# metadata: The textual data acquired from the scraper script.
	#   requires at least one field named "entries", which holds a list
	#   of metadata from each item scraped.
	def process(self, metadata: dict) -> None:
		processed_count = 0
		self.output("Starting to Download Any Media...", 0)
		self.send_status({"code": "image", "to_process_total": len(metadata["entries"]), "processed_count": 0})
		for entry in metadata["entries"]:
			# Download images and convert urls + regions to filepaths in entry["imgs"].
			# If an image cannot be downloaded, discard the image entry.
			self.output(f"Downloading Images for {entry['clean_name']}...", 0)
			check_path(PATH_MEDIA(self.platform.pid).joinpath(entry["clean_name"]))

			# Get Number of Images To Download & Send as status
			media_total = 0
			for atype in entry["imgs"]:
				media_total += len(entry["imgs"][atype])
			self.send_status({"media_total": media_total, "media_progress": 0})

			# Download Images
			media_progress = 0
			for asset_type in entry["imgs"]:
				for i in range(len(entry["imgs"][asset_type])):
					# Get URL and region
					image_url = entry["imgs"][asset_type][i][0]
					image_region = entry["imgs"][asset_type][i][1]

					# Update Status
					self.send_status({"media_current": asset_type, "media_region": image_region})

					image_path = self.download_image(image_url, asset_type, image_region, entry["clean_name"])
					if image_path != None:
						entry["imgs"][asset_type][i] = str(image_path)

						# Update Progress
						media_progress += 1
						self.send_status({"media_progress": media_progress})
					else:
						del entry["imgs"][asset_type][i]
						i -= 1

			self.send_status({"media_current": "none"})

			entry["scraped_with"] = metadata["scraped_with"]

			# Download Video (if not specified to delay video downloads until later)
			self.output(f"Checking for video download...", 0)
			if self.video_dl and "video" in entry:
				video_path: Path = self.download_video(entry["video"], entry["clean_name"])
				if self.video_downloaded:
					entry["video"] = str(video_path)

			# Convert entry to JSON and write to file
			self.output(f"Writing {entry['clean_name']} to file...", 0)
			entry_json: str = json.dumps(entry)
			check_path(PATH_META(self.platform.pid))
			with open(PATH_META(self.platform.pid).joinpath(entry["clean_name"] + ".json"), "w") as meta_file:
				meta_file.write(entry_json)

			# Update Progress
			processed_count += 1
			self.send_status({"code": "image", "processed_count": processed_count})







