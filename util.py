from typing import Callable

import flet as ft

class DropdownListTile(ft.ResponsiveRow):
	def set_dropdown_content(self, content: list[ft.dropdown.Option]):
		print("Setting Dropdown")
		self.dropdown.options = content
		if len(content) > 0:
			self.dropdown.value = content[0].key
		else:
			self.dropdown.value = None

	def __init__(self, title: str, leading_icon: ft.Icon, dropdown_options: list[ft.dropdown.Option]=[], dropdown_on_change: Callable=None):
		super().__init__()

		self.expand = True

		self.dropdown = ft.Dropdown(
			options=[],
			value="",
			col={"md": 4}
		)

		if len(dropdown_options) > 0:
			self.dropdown.options = dropdown_options
			self.dropdown.value = dropdown_options[0].key

		if dropdown_on_change != None:
			self.dropdown.on_change = dropdown_on_change

		self.controls = [
			ft.ListTile(
				leading=leading_icon,
				title=ft.Text(title),
				col={"md": 8}
			),
			self.dropdown
		]

class ResponsiveListTile(ft.ResponsiveRow):
	def __init__(self, title, leading, trailing):
		super().__init__()

		self.expand = True

		self.controls = [
			ft.Row(
				[
					leading,
					title
				],
				col={"md": 6}
			),
			ft.Row(
				[
					trailing
				],
				col={"md": 6}
			)
		]
