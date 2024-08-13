import flet as ft

from export import ExportScreen
from scrapers import MainScreen, NewScraperScreen
from settings import SettingsScreen, load_setting_file

from bsneo_scrapi.worker import Worker

class MainNavbar(ft.NavigationBar):
	def __init__(self, initial_selected, on_change):
		super().__init__()
		self.destinations = [
			ft.NavigationBarDestination(icon=ft.icons.DOWNLOADING, label="Scrape"),
			ft.NavigationBarDestination(icon=ft.icons.OPEN_IN_NEW, label="Export"),
			ft.NavigationBarDestination(icon=ft.icons.SETTINGS, label="Settings"),
		]
		self.selected_index = initial_selected
		self.on_change = on_change

def main(page: ft.Page):
	page.title = "bsneo"
	page.adaptive = True

	def view_pop(e):
		page.views.pop()
		page.update()

	def export_status(status: dict):
		if status["code"] == "finished":
			page.overlay.append(ft.SnackBar(ft.Text(f"Export Finished."), open=True))
			page.update()

	def run_export(export_options):
		# Load Settings
		settings = load_setting_file()

		def export_worker_output(msg: str, level: int):
			if level == -1:
				print(f"[DEBUG] ", end="")
			print(f"EXPORT: {msg}")

		# Initialize Worker
		worker = Worker(export_worker_output, export_status)
		worker.set_platform(export_options["system"])
		worker.set_worker_export_dest(export_options["dest"].joinpath("metadata.pegasus.txt"))
		worker.set_worker_settings(settings)

		eset = worker.set_exporter(export_options["exporter"])

		if eset == []:
			# Run Export
			print("EXPORTING NOW.")
			page.run_thread(worker.export())

	# Check if the system has allowed writes to storage.
	# This is required for proper export function.
	def check_export_permission(export_options):
		if page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS):
			# Add new PermissionHandler
			ph = ft.PermissionHandler()
			page.overlay.append(ph)
			page.update()

			# Check Storage Permission
			storage_pcheck = ph.check_permission(ft.PermissionType.STORAGE)
			print(f"Export Storage Permission: {storage_pcheck}")
			if storage_pcheck == ft.PermissionStatus.GRANTED:
				# Storage Permission Granted, continue
				run_export(export_options)
			elif storage_pcheck == ft.PermissionStatus.DENIED:
				# Storage Permission Denied, ask for permission.
				storage_preq = ph.request_permission(ft.PermissionType.STORAGE)
				if storage_preq == ft.PermissionStatus.GRANTED:
					# Permission Granted.
					run_export(export_options)
		else:
			# No Permission Needed, Continue Straight to Export
			run_export(export_options)

		# Storage Permission firmly denied, do not ask for permission.

	def open_new_page(e):
		print(vars(e))
		page.views.append(ft.View(
			controls=[
				NewScraperScreen(view_pop, page.update)
			]
		))
		page.update()

	def change_page_navbar(e):
		page_idx = e.control.selected_index
		if page_idx == 0 and not isinstance(page.controls[0], MainScreen):
			print("Switching To Scrape")
			page.controls = [MainScreen(page)]
			page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_new_page, bgcolor=ft.colors.PRIMARY, foreground_color=ft.colors.BLACK)
		elif page_idx == 1 and not isinstance(page.controls[0], ExportScreen):
			print("Switching To Export")
			page.controls = [ExportScreen(lambda _: page.update(), check_export_permission)]
			page.floating_action_button = None
		elif page_idx == 2  and not isinstance(page.controls[0], SettingsScreen):
			print("Switching To Settings")
			page.controls = [SettingsScreen()]
			page.floating_action_button = None

		page.update()

	# Navigation Bar
	page.navigation_bar = MainNavbar(0, change_page_navbar)
	page.on_view_pop = view_pop

	# Scrape Screen FAB
	page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_new_page, bgcolor=ft.colors.PRIMARY, foreground_color=ft.colors.BLACK)

	# Theming
	page.theme = ft.Theme(
		system_overlay_style=ft.SystemOverlayStyle(
			system_navigation_bar_color=ft.colors.SECONDARY_CONTAINER,
			system_navigation_bar_divider_color="#00000000"
		)
	)

	page.add(MainScreen(page))

ft.app(main)
