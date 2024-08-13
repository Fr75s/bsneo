from typing import Callable
from pathlib import Path
from bs4 import BeautifulSoup
import re, json, requests

from .paths import *
from .scraper import Scraper
from .platform import *
from .formatting import *

#
# LBScraper
# Scraper class for scraping LaunchBox
# https://gamesdb.launchbox-app.com/
#

# Constants
# LaunchBox Image Descriptor to Asset Types
LB_DESCRIPTOR_CONV = {
	"Box - Front": "boxFront",
	"Box - Back": "boxBack",
	"Box - Spine": "boxSpine",
	"Box - 3D": "box3d",
	"Disc": "cartridge",
	"Cart - Front": "cartridge",
	"Clear Logo": "logo",
	"Arcade - Marquee": "marquee",
	"Arcade - Control Panel": "panel",
	"Background Image": "background",
	"Screenshot - Gameplay": "screenshot",
	"Screenshot - Game Title": "titlescreen",
}

# LaunchBox Region to code
LB_REGION_CONV = {
	"World": "world",
	"North America": "na",
	"Canada": "ca",
	"United States": "us",
	"Japan": "jp",
	"Korea": "kr",
	"Europe": "eu",
	"United Kingdom": "uk",
	"Spain": "es",
	"France": "fr",
	"Italy": "it",
	"Germany": "de",
	"The Netherlands": "nl",
	"Russia": "ru",
	"Australia": "au",
	"New Zealand": "nz"
}

class LBScraper(Scraper):
	# Initialize Base Scraper
	def __init__(self, files: list[Path], platform: Platform, rescrape_existing: bool, send_status: Callable[dict, None], output: Callable[..., None]) -> None:
		super().__init__(files, platform, rescrape_existing, send_status, output)

	# Request the page and get its contents.
	# return: An string containing the contents of the URL; if the request failed, the string is blank.
	def fetch_page(self, link: str) -> str:
		# Request page
		page_req = None
		try:
			page_req = requests.get(link, timeout = self.FETCH_TIMEOUT)
			if page_req.status_code != 200:
				self.output(f"Fetching Search Page returned code: {page_req.status_code}", 1)
				return ""
		except Exception as e:
			self.output(f"Fetching Search Page failed: {e}", 1)
			return ""

		return page_req.text

	# Get a page that may contain a link to the game's full metadata page
	# return: A tuple with two elements.
	#   The first element contains a list of links to each found game's page.
	#   The list will be empty if no games were found.
	#   The second element indicates if the final page has been reached.
	#   If any errors occurred while searching, return (None, True).
	def get_search_page(self, link: str, games: list[str]) -> tuple[list[str], bool]:
		# Fetch page
		self.output(f"Searching for game(s) on {link}", 0)
		page_content = self.fetch_page(link)

		# Convert to HTML ETree
		page_parser = None
		try:
			page_parser = BeautifulSoup(page_content, "html.parser")
		except Exception as e:
			self.output(f"Could not convert content at {link} to BeautifulSoup: {e}", 1)
			return (None, True)

		# Check if this is the last page
		last_page: bool = page_parser.find("span", class_="current next") != None

		# Search games on page for any matches

		# Get list of games-grid-card
		card_list = page_parser.find_all("div", class_=re.compile("games-grid-card"))

		# Link to each game page from this page
		details_links: list[str] = [card.find("a")["href"] for card in card_list]#page_tree.xpath("//div[contains(@class, 'games-grid-card')]/a[1]/@href")

		# Titles of each game on this page
		titles: list[str] = [card.find("div", class_="cardTitle").h3.text for card in card_list]#page_tree.xpath("//div[@class='cardTitle']/h3[1]/text()")

		self.output(f"Finding games on this page that match...", -1)
		matched_games: list[str] = []
		for i in range(len(titles)):
			clean_title = str_to_clean(titles[i])
			for game in games:
				if clean_title == game:
					# Match Found
					self.output(f"Match found for {game}: {details_links[i]}", -1)
					matched_games.append(f"https://gamesdb.launchbox-app.com{details_links[i]}")

		return (matched_games, last_page)

	# Fetch the page containing the metadata for the game specified by link.
	# return: blank string if request failed, otherwise the page's contents.
	def get_data_page(self, link: str) -> str:
		# Fetch page
		self.output(f"Getting data from {link}", 0)
		return self.fetch_page(link)

	# Acquire metadata from data page.
	# return: A dict containing textual metadata as specified by format.md, excluding
	#   "filename" and "imgs"
	def get_metadata(self, content: str) -> dict:
		# Convert to HTML ETree
		page_parser = None
		try:
			page_parser = BeautifulSoup(content, "html.parser")
		except Exception as e:
			self.output(f"Could not convert content to BeautifulSoup: {e}", 1)
			return None

		entry = {}

		# Filename & Platform
		entry["platform"] = self.platform.pid

		# Get title
		entry["name"]: str = page_parser.find("section", class_="heroSection").find("h1").text
		#page_tree.xpath("//section[@class='heroSection']//h1/text()")[0]
		entry["clean_name"]: str = str_to_clean(entry["name"])

		# Upper Fields
		try:
			entry["rating"] = float(page_parser.find("span", id="yourRatingShort").text) / 5.0
		except:
			self.output(f"No Rating for {entry['name']}", -1)
		try:
			entry["release"] = date_to_iso(page_parser \
				.find("div", class_=re.compile("infoCards")) \
				.find("div", class_="cardHeading") \
				.find("span", string="Release Date") \
				.parent.parent.h6.text)
			#date_to_iso(page_tree.xpath("//div[contains(@class, 'infoCards')]//div[@class='cardHeading']/span[contains(.,'Release Date')]/../../h6/text()")[0])
		except:
			self.output(f"No Release Date for {entry['name']}", -1)

		# Lower Fields
		for field in ("Genres", "Developers", "Publishers"):
			try:
				entry[field.lower()] = [tag.text for tag in page_parser.find("h5", string=f"{field}").parent.find_all("a")]
				#page_tree.xpath(f"//div[@class='detailCard']/h5[contains(.,'{field}')]/../a/text()")
			except:
				self.output(f"No {field} for {entry['name']}", -1)

		try:
			entry["desc"] = page_parser \
				.find("h5", string="Overview") \
				.parent.find("p").text
			#page_tree.xpath("//div[@class='detailCard']/h5[contains(.,'Overview')]/../p/text()")[0]
			entry["desc"] = entry["desc"].replace("\r\n", "\n")
		except (IndexError, AttributeError):
			self.output(f"No Description for {entry['name']}", -1)
		try:
			entry["video"] = page_parser \
				.find("h5", string="Video") \
				.parent.find("a").text
			#page_tree.xpath("//div[@class='detailCard']/h5[contains(.,'Video')]/../a/text()")[0]
		except (IndexError, AttributeError):
			self.output(f"No Video for {entry['name']}", -1)

		self.output(f"Text Metadata Copied.", 0)
		return entry

	# Get all images from the given game's content page.
	# return: A dict containing image descriptors as keys and image urls as values.
	#   This dictionary will be placed in the metadata's "imgs" field.
	def get_images(self, content: str) -> dict[str, str]:
		# Convert to HTML ETree
		page_parser = None
		try:
			page_parser = BeautifulSoup(content, "html.parser")
		except Exception as e:
			self.output(f"Could not convert content to BeautifulSoup: {e}", 1)
			return None

		# Get Image URLs and titles from page
		imgs = {}

		image_hyperlinks = page_parser.find("div", class_=re.compile("image-list")).find_all("a")
		image_urls = [tag["href"] for tag in image_hyperlinks]#page_tree.xpath("//div[contains(@class, 'image-list')]//a/@href")
		image_titles = [tag["data-title"] for tag in image_hyperlinks]#page_tree.xpath("//div[contains(@class, 'image-list')]//a/@data-title")

		# Check titles to see if they match any descriptors
		for i in range(len(image_urls)):
			self.output(image_titles[i], -1)
			for descriptor in LB_DESCRIPTOR_CONV:
				if descriptor in image_titles[i]:
					# A descriptor matches with an existing asset, queue downloading this image
					# Get Image Region
					region = "none"
					if re.search(r"\(|\)", image_titles[i]) != None:
						region = re.search(r"\(.*?\)", image_titles[i]).group(0)[1:-1]
						if region in LB_REGION_CONV:
							region = LB_REGION_CONV[region]
						else:
							region = "none"
					# Get asset type from descriptor
					asset_type = LB_DESCRIPTOR_CONV[descriptor]
					self.output(f"Is {asset_type}", -1)

					# Add to list or init list if empty
					if asset_type in imgs:
						imgs[asset_type].append([image_urls[i], region])
					else:
						imgs[asset_type] = [[image_urls[i], region]]
					break

		# DEBUG: Output all image URLs
		for assettype in imgs:
			self.output(f"{assettype}:", -1)
			for urlrg in imgs[assettype]:
				self.output(f"\tRG: {urlrg[1]}, URL: {urlrg[0]}", -1)

		return imgs


	# Get the list of games to scrape, in cleaned name form.
	# return: The list of games to scrape.
	def get_games_to_scrape(self) -> dict[str, Path]:
		to_scrape: dict[str, Path] = {}
		for path in self.files:
			# Get clean name
			clean_name: str = path_to_clean(path)

			# Check if game was already scraped by LBScraper (if rescrape_existing is False)
			if not self.rescrape_existing:
				# Get path to metadata JSON
				game_data_path: Path = PATH_META(self.platform.pid).joinpath(clean_name + ".json")
				if game_data_path.exists():
					# Read JSON file
					with open(game_data_path, "r") as game_metadata:
						game_json = json.loads(game_metadata.read())
						# Check if scraped with LBScraper
						if "lb" in game_json["scraped_with"]:
							self.output(f"Skipping {clean_name}...", -1)
							continue

			# Add to list of games to scrape
			self.output(f"\t{path} -> {clean_name}", -1)
			to_scrape[clean_name] = path

		return to_scrape

	# Scrape game(s) via LaunchBox
	def scrape(self) -> dict:
		compiled_metadata = {
			"entries": [],
			"scraped_with": "lb",
			"error": False,
		}

		# Convert filenames to game names and purge already
		# scraped games (if rescrape_existing == False)
		self.output(f"Filtering Games Already Scraped...", -1)
		to_scrape = self.get_games_to_scrape()
		self.output(f"{to_scrape}", -1)

		# Get LaunchBox Platform ID and system URL
		lb_pid: str = self.platform.launchbox_id
		lb_url_base: str = f"https://gamesdb.launchbox-app.com/platforms/games/{lb_pid}/page/"

		# Search page checks
		page = 1
		end_reached = False

		# Set bar total
		self.send_status({"code": "search", "to_scrape_total": len(to_scrape), "found_count": 0})

		# Search across each page for this system
		self.output(f"Beginning Search for Games...", 0)
		found_count: int = 0
		while len(to_scrape) > 0 and not end_reached:
			# Update status & bar
			self.send_status({"code": "search", "details": f"Page: {page}", "found_count": found_count})
			# Scrape search page
			found_urls, end_reached = self.get_search_page(lb_url_base + str(page), to_scrape)
			page += 1

			# Check if an error occurred while searching
			if found_urls == None:
				# Handle Request error
				self.output(f"An Error Occurred while searching. Quitting...", 1)
				compiled_metadata["error"] = True
				self.send_status({"code": "error", "details": "Could Not Reach LaunchBox."})
				return compiled_metadata
			else:
				# Get metadata for each found game
				for data_page in found_urls:
					# Update Status
					self.send_status({"code": "get", "details": data_page})

					# Get textual metadata
					data_page_content: str = self.get_data_page(data_page)
					metadata = self.get_metadata(data_page_content)
					# Check if an error occurred while gathering metadata
					if metadata == None:
						self.send_status({"code": "error", "details": f"Could not gather metadata from {data_page}"})
						continue

					metadata["filename"] = to_scrape[metadata["clean_name"]].name

					# Get image links
					image_page_content: str = self.get_data_page(data_page.replace("/details/", "/images/"))
					metadata["imgs"] = self.get_images(image_page_content)
					# Check if an error occurred while gathering metadata
					if metadata["imgs"] == None:
						self.send_status({"code": "error", "details": f"Could not gather images for {metadata['name']}"})
						metadata["imgs"] = []

					# Add to metadata list
					compiled_metadata["entries"].append(metadata)

					# Delete entry in to_scrape as this game has been scraped
					del to_scrape[metadata["clean_name"]]

					# Update Status
					found_count += 1
					self.send_status({"game": metadata["name"], "found_count": found_count})

		# Set scraping progress to done
		self.send_status({"to_scrape_missing": len(to_scrape) - found_count})
		return compiled_metadata








