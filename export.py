from pathlib import Path

import flet as ft

from bsneo_scrapi.paths import PATH_BASE, check_base_path
from bsneo_scrapi.platform import PLATFORMS

from util import DropdownListTile

class ExportOptionsContainer():
	# Default Export Options
	opts = {
		"dest": None,
		"system": "",
		"exporter": "pf",
	}

	# Get the entire options dictionary
	def get_all():
		return ExportOptionsContainer.opts

	# Get a single entry in the options dictionary
	def get_entry(opt: str):
		return ExportOptionsContainer.opts[opt]

	# Set a single entry in the options dictionary
	def set_entry(opt: str, value) -> None:
		ExportOptionsContainer.opts[opt] = value

# List tile to show choice of system
class ExportConsoleListTile(DropdownListTile):
	# Update Systems Available for Export
	def update_systems(self, update_page):
		systems = []

		# Get all system folders in PATH_BASE and sort
		check_base_path()

		# Get names of systems and add to dropdown menu
		for system_dir in PATH_BASE.iterdir():
			if system_dir.is_dir():
				print(f"System available for Export: {system_dir.name}")
				system_longname = PLATFORMS[system_dir.name].fullname
				systems.append(ft.dropdown.Option(key=system_dir.name, text=system_longname))

		# Sort Systems
		systems = sorted(systems, key=lambda option: option.text)

		self.set_dropdown_content(systems)

		# self.trailing.options = systems
		# # Set initial value of dropdown
		# if len(systems) > 0:
		# 	self.trailing.value = systems[0].key

		# Set "system" option entry
		ExportOptionsContainer.set_entry("system", systems[0].key)
		ExportScreen.update_export_status()

	# Change the currently chosen system
	def choose_system(self, e):
		ExportOptionsContainer.set_entry("system", e.control.value)
		ExportScreen.update_export_status()

	# Init
	def __init__(self, update_page):
		# Set standard properties

		# Initialize blank Dropdown, then update via update_systems
		# self.trailing = ft.Dropdown(
		# 	options=[],
		# 	value="",
		# 	on_change=self.choose_system,
		# 	width=250,
		# )

		super().__init__("System", ft.Icon(ft.icons.GAMEPAD))

		self.dropdown.on_change = self.choose_system
		self.update_systems(update_page)

class ExportDestListTile(ft.ListTile):
	# Set destination on file picker select
	def on_select(self, e: ft.FilePickerResultEvent):
		if e.path != None:
			print(f"Setting Destination to {e.path}")
			# Set value in label
			self.trailing.value = e.path
			ExportOptionsContainer.set_entry("dest", Path(e.path))
			# Page Update
			ExportScreen.update_export_status()

	# Init
	def __init__(self, file_picker, on_click):
		super().__init__()

		# Set standard properties
		self.title = ft.Text("Destination")
		self.height = 50
		self.leading = ft.Icon(ft.icons.FOLDER)

		# Handle File Picker + Update
		self.on_click = on_click
		file_picker.on_result = self.on_select

		# Default Trailing Text
		self.trailing = ft.Text("< Select Output Destination >")

class ExportScreen(ft.SafeArea):
	# Export Status Label
	export_status = ft.Text(
		"NOT READY",
		size=16
	)

	# Export Action Button
	export_button = ft.FilledButton(
		"Export Now",
		disabled=True,
		icon=ft.icons.OPEN_IN_NEW,
		height=50
	)

	update = None

	# Update status label and enable button if ready
	def update_export_status():
		# No Destination Selected
		missing = []
		if ExportOptionsContainer.get_entry("dest") == None:
			missing.append("No Destination Selected")

		# No System Selected
		if ExportOptionsContainer.get_entry("system") == "":
			missing.append("No System Selected")

		if len(missing) > 0:
			# Some Elements are Missing
			# Prepare Missing Details
			full_msg = "Not Ready: "
			for issue in missing:
				full_msg += issue + ", "
			full_msg = full_msg[:-2]
			# Show Missing Details
			ExportScreen.export_status.value = full_msg
			ExportScreen.export_button.disabled = True
		else:
			# No Elements are Missing
			# Enable Button
			ExportScreen.export_status.value = "Ready to Export"
			ExportScreen.export_button.disabled = False

		# Refresh Page
		ExportScreen.update(None)

	def __init__(self, update, run_export):
		# Set Page Refresh Function
		ExportScreen.update = update

		# Define File Picker and set file select button to pick folder
		exporter_fp = ft.FilePicker()
		edlt = ExportDestListTile(exporter_fp, lambda _: exporter_fp.get_directory_path())

		# Set Initial Export Status
		ExportScreen.update_export_status()

		# Run Export on button click
		ExportScreen.export_button.on_click = lambda _: run_export(ExportOptionsContainer.get_all())

		self.content = ft.ListView([
			# File Picker
			exporter_fp,

			# Header
			ft.Text(
				"Export",
				size=26,
			),
			ft.Divider(),

			# Export Options
			# Set Output Directory
			edlt,
			# Set System
			ExportConsoleListTile(update),
			# Set Format
			DropdownListTile(
				"Export Format",
				ft.Icon(ft.icons.DESCRIPTION),
				[
					ft.dropdown.Option(key="pf", text="Pegasus")
				],
				lambda e: ExportOptionsContainer.set_entry("exporter", e.control.value),
			),
			ft.Divider(),

			# Export Status
			self.export_status,
			# Begin Export Button
			ExportScreen.export_button,
		],
		spacing = 8,
		padding = ft.padding.symmetric(horizontal=4),
		expand = True
		)

		super().__init__(self.content)
		self.expand = True
