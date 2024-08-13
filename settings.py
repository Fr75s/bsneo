from pathlib import Path

import json
import flet as ft

from bsneo_scrapi.paths import PATH_CONFIG, check_config_path
from bsneo_scrapi.region import REGIONS

from util import DropdownListTile

# Class that contains all settings
class SettingContainer():
	# Initial Setting Values
	settings = {
		"rescrape_existing": False,
		"region": "none",
		"strict_region": False,
		"video_dl": True
	}

	# Get the entire settings dictionary
	def get_all_settings():
		return SettingContainer.settings

	# Get a single entry in the settings dictionary
	def get_setting(setting: str):
		return SettingContainer.settings[setting]

	# Set a single entry in the settings dictionary
	def set_setting(setting: str, value) -> None:
		SettingContainer.settings[setting] = value

# Single Setting List Entry Class
class Setting(ft.ListTile):
	# Instance Variables
	setting = ""
	setting_type = ""

	# Change this setting's value
	def change_setting(self, event):
		print(f"Changing Setting {self.setting}")

		# Change setting in SettingContainer
		new_value = self.trailing.value
		SettingContainer.set_setting(self.setting, new_value)

		# Write to file
		with open(PATH_CONFIG, "w") as cfg_file:
			cfg_file.write(json.dumps(SettingContainer.get_all_settings()))

	# Initialize setting appearance and get initial value
	def __init__(self, setting_type: str, setting: str, setting_label: str, icon, setting_data: dict = {}):
		super().__init__()

		# Set Setting Name and Icon
		self.leading = ft.Icon(icon)
		self.title = ft.Text(setting_label)

		# Get initial value for this setting
		self.setting = setting
		self.setting_type = setting_type
		setting_value = SettingContainer.get_setting(self.setting)
		print(f"Initializing Setting {setting} to {setting_value}")

		# Boolean Setting Switch
		if setting_type == "bool":
			self.toggle_inputs = True
			self.trailing = ft.Switch(value=setting_value, on_change=self.change_setting)

		# List Setting Dropdown
		# Requires setting_data["list"]
		if setting_type == "list":
			dropdown_items = []
			for item in setting_data["list"]:
				dropdown_items.append(ft.dropdown.Option(item))

			self.trailing = ft.Dropdown(
				options=dropdown_items,
				on_change=self.change_setting,
				value=setting_value,
				width=250
			)

class SettingsScreen(ft.SafeArea):
	def change_setting(self, setting: str, value):
		print(f"Changing Setting {setting}")

		# Change setting in SettingContainer
		SettingContainer.set_setting(setting, value)

		# Write to file
		with open(PATH_CONFIG, "w") as cfg_file:
			cfg_file.write(json.dumps(SettingContainer.get_all_settings()))

	def __init__(self):
		# Load settings from file
		load_settings()

		self.content = ft.ListView([
			# Header
			ft.Text(
				"Settings",
				size=26,
			),
			ft.Divider(),

			# General Settings
			ft.Text(
				"General",
				size=20,
			),
			Setting("bool", "video_dl", "Download Videos", ft.icons.VIDEOCAM),
			Setting("bool", "rescrape_existing", "Re-Scrape Already Scraped", ft.icons.REFRESH),
			ft.Divider(),

			# Region Settings
			ft.Text(
				"Region",
				size=20,
			),
			DropdownListTile(
				"Region",
				ft.Icon(ft.icons.PUBLIC),
				[ft.dropdown.Option(key=region, text=region.upper()) for region in REGIONS],
				lambda e: self.change_setting("region", e.control.value)
			),
			#Setting("list", "region", "Region", ft.icons.PUBLIC, {"list": REGIONS}),
			Setting("bool", "strict_region", "Strict Region Filter", ft.icons.LOCK),
		],
		spacing = 8,
		padding = ft.padding.symmetric(horizontal=4),
		expand = True,
		)

		super().__init__(self.content)
		self.expand = True

# Loads settings from the JSON file at PATH_CONFIG.
def load_setting_file() -> dict:
	print("Loading Settings...")

	if PATH_CONFIG.exists():
		with open(PATH_CONFIG, "r") as cfg_file:
			try:
				print("Settings Successfully Loaded.")
				return json.loads(cfg_file.read())
			except:
				print("Could not load settings.")
	else:
		print("Settings file does not exist. Initializing...")
		check_config_path()
		with open(PATH_CONFIG, "w") as cfg_file:
			cfg_file.write(json.dumps(SettingContainer.get_all_settings))

	return {}

# Loads settings then sets all settings
def load_settings():
	print("Loading Settings...")

	settings = load_setting_file()
	for key in settings:
		SettingContainer.set_setting(key, settings[key])
