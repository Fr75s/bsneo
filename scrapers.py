from typing import Callable
from pathlib import Path

import flet as ft

from bsneo_scrapi.worker import Worker
from bsneo_scrapi.platform import PLATFORMS

from settings import load_setting_file
from util import DropdownListTile

# Constants
# File Extensions ignored by file scanner in "Choose Folder" dialog
IGNORED_EXTENSIONS = (
	".txt",
	".bak"
)

# Status Codes to Status Labels
STATUS_CODE_CONV = {
	"idle": "Idle",
	"hash": "Processing Hashes",
	"search": "Searching for Games",
	"get": "Scraping Game Pages",
	"image": "Downloading Images",
	"video": "Downloading Video",
	"finished": "Finished",
	"error": "Error"
}

# Scraper short codes to full names
SCRAPER_TYPE_CONV = {
	"lb": "LaunchBox"
}

# Container class for a bsneo_scrapi Worker.
# Additionally sends the worker's status to ScraperList.
class ScraperInterface():
	# Send this worker's status to ScraperList.
	def status_update(self, status: dict):
		self.update_status(status)

	# Initialize Worker
	def __init__(self, worker_cfg: dict, scraper_id: str, update_status: Callable[dict, None]):
		# Update Status in GUI
		self.update_status = update_status

		self.status = "idle"

		# Log output for this worker
		def scrape_worker_output(msg: str, level: int):
			if level == -1:
				print(f"[DEBUG] ", end="")
			print(f"SCRAPE ({scraper_id}): {msg}")

		# Init Worker
		self.scraper_id = scraper_id
		self.worker = Worker(scrape_worker_output, self.status_update)

		self.worker.set_platform(worker_cfg["pid"])
		self.worker.set_worker_files(worker_cfg["files"])
		self.worker.set_worker_settings(load_setting_file())

		sset = self.worker.set_scraper(worker_cfg["scraper"])
		if sset == []:
			print(f"Worker {scraper_id} Ready.")

		self.scraper_type = worker_cfg["scraper"]

# UI Class for a Screen featuring extra details regarding a ScraperInterface.
class ScraperScreen(ft.ListView):
	# Confirm whether or not to dismiss this scraper
	def dismiss_scraper(self, e) -> None:
		if self.scraper.worker.status['code'] == "finished":
			# This Scraper is Finished, No need to confirm.
			self.page.views.pop()
			self.dismiss(None)
		else:
			# Confirm Via Alert Dialog.

			# Close dialog if No, otherwise dismiss this scraper
			def close_dialog(e):
				if e.control.text == "Yes":
					self.page.views.pop()
					self.dismiss(None)
				else:
					self.page.close(confirm_dialog)

			# Initialize the dialog
			confirm_dialog = ft.AlertDialog(
				modal=True,
				title=ft.Text("Are You Sure?"),
				content=ft.Text("If you cancel scraping now, the scraped data may not be saved."),
				actions=[
					ft.TextButton("Yes", on_click=close_dialog),
					ft.TextButton("No", on_click=close_dialog),
				],
				actions_alignment=ft.MainAxisAlignment.END,
			)

			# Open confirmation dialog
			self.page.open(confirm_dialog)

	# Updates the status values shown on screen.
	def update_status(self, status: dict) -> None:
		# Update Status Label
		self.status_label.value = f"Current Status: {STATUS_CODE_CONV[status['code']]}"
		if "details" in status:
			self.status_details_label.value = status['details']

		# Searching & Scraping Progress Bar & Label
		if "to_scrape_total" in status:
			self.search_scrape_total = status["to_scrape_total"]
		if "found_count" in status:
			self.search_scrape_progress = status["found_count"]
			if self.search_scrape_total > 0:
				self.search_scrape_label.value = f"Games Found: {self.search_scrape_progress}/{self.search_scrape_total}"
				self.search_scrape_bar.value = self.search_scrape_progress / self.search_scrape_total
			else:
				self.search_scrape_bar.value = 1.0

		# Media Processing Progress Bar & Label
		if "to_process_total" in status:
			self.processed_total = status["to_process_total"]
		if "processed_count" in status:
			self.processed_progress = status["processed_count"]
			if self.processed_total > 0:
				self.processed_label.value = f"Games with Downloaded Media: {self.processed_progress}/{self.processed_total}"
				self.processed_bar.value = self.processed_progress / self.processed_total
			else:
				self.processed_bar.value = 1.0

		# Individual Media Download Progress Bar & Label
		if "media_total" in status:
			self.media_download_total = status["media_total"]
		if "media_current" in status:
			self.media_download_progress = status["media_progress"]
			if status["media_current"] != "none":
				if self.media_download_total > 0:
					self.media_download_label.value = f"Downloading {status['media_current']} ({self.media_download_progress}/{self.media_download_total})"
					self.media_download_bar.value = self.media_download_progress / self.media_download_total
				else:
					self.media_download_bar.value = 1.0
			else:
				self.media_download_label.value = f"All Images Downloaded."
				self.media_download_bar.value = 1.0

		# Video Download Progress Bar & Label
		if "video_progress" in status:
			self.video_download_progress = status["video_progress"]
			if self.video_download_progress == 0.0 or self.video_download_progress == -2.0:
				# Video download progress is 0, there is no video present.
				self.video_download_label.value = "No Video to Download."
				self.video_download_bar.value = 0.0
			elif self.video_download_progress < 1:
				# There is a video to download
				self.video_download_label.value = "Downloading Video"
				# Check if there is actual progress
				if self.video_download_progress > 0:
					# Actual progress reported, show on the progress bar
					self.video_download_bar.value = self.video_download_progress
				elif self.video_download_progress >= -1.5:
					# No progress reported, show progress bar as indeterminate
					self.video_download_bar.value = None
			else:
				# Video download progress is >= 1, therefore a video was present and has finished downloading.
				self.video_download_label.value = "Video Download Finished."

		# Update Page
		self.page.update()

	def __init__(self, scraper: ScraperInterface, page: ft.Page, dismiss: Callable, pop: Callable):
		super().__init__()

		# Initialize class vars used elsewhere
		self.scraper = scraper
		self.page = page
		self.dismiss = dismiss

		# Set Root UI Details
		self.spacing = 8
		self.expand = True

		# Current Status and status details UI Definitions
		self.status_label = ft.Text(
			f"Current Status: {STATUS_CODE_CONV[self.scraper.worker.status['code']]}",
			size=20,
		)
		self.status_details_label = ft.Text(
			f"",
			size=18,
		)

		# Remote Game Search + Scrape Progress Bar and Label
		self.search_scrape_total: int = 0
		self.search_scrape_progress: int = 0
		self.search_scrape_label: ft.Text = ft.Text(
			"No Games to Be Found.",
			size=18,
		)
		self.search_scrape_bar: ft.ProgressBar = ft.ProgressBar(
			value=0.0,
			border_radius=ft.border_radius.all(2),
		)

		# Game Save Progress Bar and Label
		self.processed_total: int = 0
		self.processed_progress: int = 0
		self.processed_label: ft.Text = ft.Text(
			"No Games with Media to Download.",
			size=18,
		)
		self.processed_bar: ft.ProgressBar = ft.ProgressBar(
			value=0.0,
			border_radius=ft.border_radius.all(2),
		)

		# Image Downloads for 1 game Progress Bar and Label
		self.media_download_total: int = 0
		self.media_download_progress: int = 0
		self.media_download_label: ft.Text = ft.Text(
			"No Images to Download.",
			size=18,
		)
		self.media_download_bar: ft.ProgressBar = ft.ProgressBar(
			value=0.0,
			border_radius=ft.border_radius.all(2),
		)

		# Video Download Progress Bar and Label
		self.video_download_progress: int = 0
		self.video_download_label: ft.Text = ft.Text(
			"No Video to Download.",
			size=18,
		)
		self.video_download_bar: ft.ProgressBar = ft.ProgressBar(
			value=0.0,
			border_radius=ft.border_radius.all(2),
		)

		# Immediately update default statuses based on the actual current status.
		self.update_status(self.scraper.worker.status)

		# Control Layout
		self.controls = [
			# Header Row
			ft.ResponsiveRow(
				alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
				expand=True,
				controls=[
					# Title and Back Button
					ft.Row(
						spacing=10,
						col={"md": 6},
						controls=[
							# Back Button
							ft.IconButton(
								icon = ft.icons.ARROW_BACK,
								icon_color = ft.colors.ON_SURFACE,
								icon_size = 30,
								tooltip = "Back",
								on_click = pop
							),
							# Title
							ft.Text(
								f"{self.scraper.worker.platform.fullname} ({SCRAPER_TYPE_CONV[self.scraper.scraper_type]})",
								size=26,
							)
						]
					),
					# Dismiss Label and Button
					ft.Row(
						spacing=10,
						col={"md": 6},
						alignment=ft.MainAxisAlignment.END,
						controls=[
							ft.Text(
								"Dismiss",
								size=22,
							),
							ft.IconButton(
								icon = ft.icons.CLEAR,
								icon_color = ft.colors.ON_SURFACE,
								icon_size = 30,
								tooltip = "Dismiss Scraper",
								on_click = self.dismiss_scraper,
							)
						]
					)
				]
			),
			ft.Divider(),

			# Quick Status
			self.status_label,
			self.status_details_label,
			ft.Divider(),

			# Found Metadata Progress
			self.search_scrape_label,
			self.search_scrape_bar,

			# All Games Media Download Progress
			self.processed_label,
			self.processed_bar,

			# Single Game Media Download Progress
			self.media_download_label,
			self.media_download_bar,

			# Single Game Video Download Progress
			self.video_download_label,
			self.video_download_bar,
		]

# UI Component for a single entry in the list of all Scrapers.
class ScraperListEntry(ft.Container):
	# Set the value of the status label (subtitle).
	def set_status(self, status: str):
		self.subtitle.value = status

	def __init__(self, scraper_id, pid, scraper_type, open_scraper):
		super().__init__()

		# Graphical Padding
		self.padding = 12

		# Scraper ID from ScraperList
		self.scraper_id = scraper_id

		# Define Components
		# Title
		self.title: ft.Text = ft.Text(
			f"{PLATFORMS[pid].fullname} ({SCRAPER_TYPE_CONV[scraper_type]})",
			size=18,
		)
		# Status
		self.subtitle: ft.Text = ft.Text(
			"Idle",
			size=14,
		)
		# Quick Progress Bar
		self.pbar: ft.ProgressBar = ft.ProgressBar(
			value=0.0,
			border_radius=ft.border_radius.all(2),
		)
		self.to_scrape_total = 1
		self.to_process_total = 1

		# Finished Icon
		self.status_icon: ft.Icon = ft.Icon(
			name=ft.icons.CHECK,
			color=ft.colors.SURFACE_VARIANT,
			size=30,
		)

		# Arrangement
		self.content = ft.Row([
			ft.Column(
				spacing = 2,
				expand = True,
				controls = [
					self.title,
					self.subtitle,
					self.pbar,
				]
			),
			ft.Container(
				self.status_icon,
				padding=ft.padding.only(left=30)
			)
		])

		# UI Component Details
		self.border_radius = 8
		self.ink = True
		# Click to open a ScraperScreen based on this scraper.
		self.on_click = lambda _: open_scraper(scraper_id)

# UI Component Class for all ScraperListEntries + Manager for all ScraperInterfaces.
# Responsible for managing all Scrapers.
class ScraperList(ft.ListView):
	# Reference to Main Page
	page: ft.Page = None
	current_scraper_screen: ScraperScreen = None

	# Static variable to store number of scrapers made, used as an ID for each scraper
	scraper_inc: int = 0
	scrapers: dict[str, ScraperInterface] = {}

	# Removes the given scraper with scraper_id from the list of scrapers.
	def remove_scraper_entry(self, scraper_id: str) -> None:
		# Remove Scraper from controls
		for i in range(len(self.controls)):
			if self.controls[i].scraper_id == scraper_id:
				del self.controls[i]
				break
		# Remove Scraper from scraper interface list
		del self.scrapers[scraper_id]
		self.current_scraper_screen = None
		self.page.update()

	# Get the ScraperListEntry with ID scraper_id from self.controls.
	def get_scraper_entry(self, scraper_id: str) -> ScraperListEntry:
		for sle in self.controls:
			if sle.scraper_id == scraper_id:
				return sle

	# Update the ScraperListEntry corresponding to scraper_id based on the given status.
	def update_scraper(self, scraper_id: str, status: dict) -> None:
		#print(f"Updating Status for {scraper_id}: {status}")
		scraper = self.scrapers[scraper_id]

		# Update List Entry
		list_entry = self.get_scraper_entry(scraper_id)
		list_entry.set_status(STATUS_CODE_CONV[status["code"]])
		match status["code"]:
			# Update first half of bar: Search Progress
			case "search" | "get":
				if "to_scrape_total" in status:
					list_entry.to_scrape_total = status["to_scrape_total"]
				if list_entry.to_scrape_total > 0:
					list_entry.pbar.value = 0.5 * (status["found_count"] / list_entry.to_scrape_total)
				else:
					list_entry.pbar.value = 0.5
			# Update Second half of bar: Image Download Progress
			case "image":
				if "to_process_total" in status:
					list_entry.to_process_total = status["to_process_total"]
				if list_entry.to_process_total > 0:
					list_entry.pbar.value = 0.5 + 0.5 * (status["processed_count"] / list_entry.to_process_total)
				else:
					list_entry.pbar.value = 1.0
			# Finished Scraping
			case "finished":
				list_entry.pbar.value = 1.0
				list_entry.status_icon.color = ft.colors.SURFACE_TINT

		# Update Scraper Screen (if set and if it matches the scraper being updated)
		if self.current_scraper_screen != None and self.current_scraper_screen.scraper.scraper_id == scraper_id:
			self.current_scraper_screen.update_status(status)

		self.page.update()

	# Exits the current scraper screen and destroys it.
	def pop_scraper(self, e) -> None:
		self.page.views.pop()
		self.current_scraper_screen = None
		self.page.update()

	# Open the page for the given scraper
	def open_scraper(self, scraper_id: str) -> None:
		print(f"Opening Details for {scraper_id}")
		# Create the new ScraperScreen
		self.current_scraper_screen = ScraperScreen(
			self.scrapers[scraper_id],
			self.page,
			lambda _: self.remove_scraper_entry(scraper_id),
			self.pop_scraper,
		)
		# Add the new ScraperScreen to the View list
		self.page.views.append(ft.View(
			controls=[
				self.current_scraper_screen,
			]
		))
		self.page.update()

	# Add a new Scraper to the list of scrapers
	def add_scraper(self, cfg) -> None:
		# Get ID
		scraper_id = str(ScraperList.scraper_inc)
		ScraperList.scraper_inc += 1

		# Init New Scraper Interface with cfg
		new_scraper = ScraperInterface(
			cfg,
			scraper_id,
			lambda new_status: self.update_scraper(scraper_id, new_status)
		)

		# Add ScraperInterface to ScraperInterface dict with corresponding ID
		self.scrapers[scraper_id] = new_scraper
		# Add new ScraperListEntry corresponding to the new ScraperInterface
		self.controls.append(ScraperListEntry(scraper_id, cfg["pid"], cfg["scraper"], self.open_scraper))

		self.page.update()

		# Run the new scraper
		print(f"RUNNING SCRAPER {scraper_id}")
		worker = new_scraper.worker
		self.page.run_thread(worker.run())

	def __init__(self, page) -> None:
		super().__init__()

		# Quick reference to main.page
		self.page = page

		# UI Component Details
		self.spacing = 8
		self.expand = True

		# Initialize with empty list.
		self.controls = []
		self.current_scraper_screen = None

		# # DEBUG
		# self.add_scraper({
		# 	"pid": "virtualboy",
		# 	"files": [Path("/mnt/Emulation/lib/VRB/Mario Clash (Japan, USA).vb"), Path("/mnt/Emulation/lib/VRB/3-D Tetris (USA).vb")],
		# 	"scraper": "lb"
		# })

# UI Component Class that contains the ScraperList.
class MainScreen(ft.SafeArea):
	slist: ScraperList = None
	page: ft.Page = None

	def __init__(self, page):
		# Initialize ScraperList
		if MainScreen.slist == None:
			MainScreen.slist = ScraperList(page)
		MainScreen.page = page

		self.content = ft.ListView([
			# Scrape Screen Header
			ft.Text(
				"Scrapers",
				size=26,
			),
			ft.Divider(),

			# ScraperList
			MainScreen.slist
		],
		spacing = 8,
		padding = ft.padding.symmetric(horizontal=4),
		expand = True,
		)

		super().__init__(self.content)

# Custom UI Component for the system select ListTile in NewScraperScreen.
class NewScraperSystem(DropdownListTile):
	def __init__(self, set_system):
		super().__init__("System", ft.Icon(ft.icons.GAMEPAD), [], lambda e: set_system(e.control.value))

		# Get list of systems as Dropdown Options
		system_list = []
		for platform in PLATFORMS:
			system_list.append(ft.dropdown.Option(key=platform, text=PLATFORMS[platform].fullname))
		system_list = sorted(system_list, key=lambda option: option.text)

		# Set initial system
		set_system(system_list[0].key)

		self.set_dropdown_content(system_list)

		# Initialize Dropdown using list of systems
		# self.trailing = ft.Dropdown(
		# 	options=system_list,
		# 	value = system_list[0].key,
		# 	on_change=lambda e: set_system(e.control.value),
		# 	width=250,
		# )

# Defines a Screen where new Scrapers can be added to the ScraperList.
class NewScraperScreen(ft.SafeArea):
	# Refresh Page
	update = None
	view_pop = None

	# Scraper Configuration
	# Store Config
	current_config: dict = {
		"scraper": "lb"
	}

	# Set Configuration Key:Value Pair
	def set_cfg(key: str, value):
		NewScraperScreen.current_config[key] = value

	# Get Configuration Value
	def get_cfg(key: str):
		return NewScraperScreen.current_config[key]

	# Check if config has a given entry with the given key
	def has_cfg(key: str):
		return key in NewScraperScreen.current_config


	# File Count Label
	file_count_label: ft.Text = ft.Text(
		"No Files Selected"
	)

	# Update the File Count Label's contents + The Scrape Button
	def update_file_count(self):
		# Get number of files from file list
		file_count = len(NewScraperScreen.get_cfg("files"))
		# Enable Scrape Button if there are files
		self.action_button.disabled = file_count == 0
		# Update File Count Label
		if file_count > 0:
			self.file_count_label.value = f"{file_count} Files Selected"
		else:
			self.file_count_label.value = "No Files Selected"
		# Update Page
		NewScraperScreen.update()

	# Reset Files in config
	def reset_files(self):
		NewScraperScreen.set_cfg("files", [])
		self.update_file_count()

	# Adds chosen files to current config's File list.
	def fp_chosen_file(self, e: ft.FilePickerResultEvent):
		if e.files or e.path:
			# Init file list to already selected, if it exists
			file_list = []
			if NewScraperScreen.has_cfg("files"):
				file_list = NewScraperScreen.get_cfg("files")

			if e.files:
				# Convert selected files to path objects
				for f in e.files:
					# Block files already in list
					path = Path(f.path)
					if not path in file_list:
						file_list.append(path)
			elif e.path:
				# Convert game files in e.path to path objects
				parent_dir = Path(e.path)
				for f in parent_dir.iterdir():
					# Block Directories, non-game files, and files already in list
					if not (f.is_dir() or f.suffix in IGNORED_EXTENSIONS) and not f in file_list:
						file_list.append(Path(f))

			print(f"FILES: {file_list}")

			# Add files
			NewScraperScreen.set_cfg("files", file_list)
			self.update_file_count()

	# Add the New Scraper to the ScraperList, and handle UI Actions
	def add_scraper(e):
		# Close NewScraperScreen
		NewScraperScreen.view_pop(e)
		# Notify user via SnackBar about new scraper.
		MainScreen.page.overlay.append(ft.SnackBar(ft.Text(f"Scraper Added."), open=True))
		# Add to ScraperList with current configuration
		MainScreen.slist.add_scraper(NewScraperScreen.current_config)

	# Scrape Action Button
	action_button = ft.FilledButton(
		"Begin Scraping",
		disabled=True,
		icon=ft.icons.DOWNLOADING,
		height=50,
		on_click=add_scraper,
	)

	def __init__(self, view_pop, update):
		# Update & View pop page functions
		NewScraperScreen.update = update
		NewScraperScreen.view_pop = view_pop

		# FilePicker Component for selecting files to scrape
		scraper_fp = ft.FilePicker(on_result = self.fp_chosen_file)
		# System Select ListTile via NewScraperSystem
		system_listtile = NewScraperSystem(lambda v: NewScraperScreen.set_cfg("pid", v))

		# Refresh page with new components
		NewScraperScreen.update()

		self.content = ft.ListView(
		[
			scraper_fp,

			# Header Row
			ft.Row(
				spacing=10,
				controls=[
					ft.IconButton(
						icon = ft.icons.ARROW_BACK,
						icon_color = ft.colors.ON_SURFACE,
						icon_size = 30,
						tooltip = "Back",
						on_click = view_pop
					),
					ft.Text(
						"New Scraper",
						size=26,
					)
				]
			),
			ft.Divider(),

			# Config List Tiles
			# File Count ListTile
			ft.ListTile(
				title=ft.Text("Files"),
				height=50,
				leading=ft.Icon(ft.icons.FOLDER),
				trailing = self.file_count_label,
			),
			# File Select Buttons
			ft.Row(
				[
					# Choose Folder
					ft.OutlinedButton(
						text="Choose Folder",
						icon=ft.icons.FOLDER,
						on_click=lambda _: scraper_fp.get_directory_path(),
					),
					# Choose Files
					ft.OutlinedButton(
						text="Choose Files",
						icon=ft.icons.FILE_COPY,
						on_click=lambda _: scraper_fp.pick_files(allow_multiple=True),
					),
					# Clear Files
					ft.OutlinedButton(
						text="Clear Files",
						icon=ft.icons.CLEAR,
						on_click=lambda _: self.reset_files(),
					),
				],
				# Row UI Details
				wrap=True,
				spacing=8,
			),
			# System Select ListTile
			system_listtile,
			# Scraper Select ListTile
			DropdownListTile(
				"Scraper",
				ft.Icon(ft.icons.LANGUAGE),
				[
					ft.dropdown.Option(key="lb", text="LaunchBox")
				],
				lambda e: NewScraperScreen.set_cfg("scraper", e.control.value),
			),
			ft.Divider(),

			self.action_button
		],
		spacing = 8,
		padding = ft.padding.symmetric(horizontal=4),
		expand = True,
		)

		super().__init__(self.content)
		self.expand = True
