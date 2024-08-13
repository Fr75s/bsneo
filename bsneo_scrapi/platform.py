#
# Platform
# Class to quickly access platform data
#
# PLUS: platforms: List of platforms
#

class Platform():
	# Short platform name
	pid: str = ""
	# Full platform name
	fullname: str = ""

	# Launchbox Platform URL component (blank if not present)
	launchbox_id: str = ""

	# Screenscraper Platform ID (0 if not present)
	screenscraper_id: int = 0

	def __init__(self, pid: str, fn: str, lb: str, sc: int) -> None:
		self.pid = pid
		self.fullname = fn
		self.launchbox_id = lb
		self.screenscraper_id = sc

# Dictionary of every platform (indexed by platform ID)
PLATFORMS: dict[str, Platform] = {
	"3do": Platform("3do", "3DO Interactive Multiplayer", "1-3do-interactive-multiplayer", 29),
	"amiga": Platform("amiga", "Commodore Amiga", "2-commodore-amiga", 64),
	"amstradcpc": Platform("amstradcpc", "Amstrad CPC", "3-amstrad-cpc", 65),
	"android": Platform("android", "Android", "4-android", 0),
	"arcade": Platform("arcade", "Arcade", "5-arcade", 0),
	"atari2600": Platform("atari2600", "Atari 2600", "6-atari-2600", 26),
	"atari5200": Platform("atari5200", "Atari 5200", "7-atari-5200", 40),
	"atari7800": Platform("atari7800", "Atari 7800", "8-atari-7800", 41),
	"atarijaguar": Platform("atarijaguar", "Atari Jaguar", "9-atari-jaguar", 27),
	"atarijaguarcd": Platform("atarijaguarcd", "Atari Jaguar CD", "10-atari-jaguar-cd", 0),
	"atarilynx": Platform("atarilynx", "Atari Lynx", "11-atari-lynx", 28),
	"atarixe": Platform("atarixe", "Atari XEGS", "12-atari-xegs", 0),
	"atarist": Platform("atarist", "Atari ST", "76-atari-st", 42),
	"colecovision": Platform("colecovision", "Colecovision", "13-colecovision", 48),
	"adam": Platform("adam", "Coleco ADAM", "117-coleco-adam", 89),
	"c64": Platform("c64", "Commodore 64", "14-commodore-64", 66),
	"c128": Platform("c128", "Commodore 128", "118-commodore-128", 0),
	"amigacd32": Platform("amigacd32", "Commodore Amiga CD32", "119-commodore-amiga-cd32", 130),
	"amigacdtv": Platform("amigacdtv", "Commodore Amiga CDTV", "120-commodore-cdtv", 129),
	"vic20": Platform("vic20", "Commodore VIC-20", "122-commodore-vic-20", 73),
	"intellivision": Platform("intellivision", "Mattel Intellivision", "15-mattel-intellivision", 115),
	"ios": Platform("ios", "Apple iOS", "16-apple-ios", 0),
	"macintosh": Platform("macintosh", "Apple macOS", "17-apple-mac-os", 146),
	"vectrex": Platform("vectrex", "GCE Vectrex", "125-gce-vectrex", 102),
	"xbox": Platform("xbox", "Microsoft Xbox", "18-microsoft-xbox", 32),
	"xbox360": Platform("xbox360", "Microsoft Xbox 360", "19-microsoft-xbox-360", 33),
	"xboxone": Platform("xboxone", "Microsoft Xbox One", "20-microsoft-xbox-one", 34),
	"xboxseries": Platform("xboxseries", "Microsoft Xbox Series X/S", "222-microsoft-xbox-series-xs", 0),
	"dos": Platform("dos", "Microsoft DOS", "83-ms-dos", 135),
	"msx": Platform("msx", "Microsoft MSX", "82-microsoft-msx", 113),
	"msx2": Platform("msx2", "Microsoft MSX2", "190-microsoft-msx2", 116),
	"windows": Platform("windows", "Microsoft Windows", "84-windows", 138),
	"linux": Platform("linux", "Linux", "218-linux", 145),
	"ngp": Platform("ngp", "SNK Neo Geo Pocket", "21-snk-neo-geo-pocket", 25),
	"ngpc": Platform("ngpc", "SNK Neo Geo Pocket Color", "22-snk-neo-geo-pocket-color", 82),
	"neogeo": Platform("neogeo", "SNK Neo Geo", "23-snk-neo-geo-aes", 142),
	"3ds": Platform("3ds", "Nintendo 3DS", "24-nintendo-3ds", 17),
	"n64": Platform("n64", "Nintendo 64", "25-nintendo-64", 14),
	"64dd": Platform("64dd", "Nintendo 64DD", "194-nintendo-64dd", 122),
	"nds": Platform("nds", "Nintendo DS", "26-nintendo-ds", 15),
	"nes": Platform("nes", "Nintendo Entertainment System", "27-nintendo-entertainment-system", 3),
	"fds": Platform("fds", "Famicom Disk System", "157-nintendo-famicom-disk-system", 106),
	"snes": Platform("snes", "Super Nintendo Entertainment System", "53-nintendo-entertainment-system", 4),
	"gameandwatch": Platform("gameandwatch", "Nintendo Game & Watch", "166-nintendo-game-watch", 52),
	"gb": Platform("gb", "Nintendo Game Boy", "28-nintendo-game-boy", 9),
	"gba": Platform("gba", "Nintendo Game Boy Advance", "29-nintendo-game-boy-advance", 12),
	"gbc": Platform("gbc", "Nintendo Game Boy Color", "30-nintendo-game-boy-color", 10),
	"gc": Platform("gc", "Nintendo GameCube", "31-nintendo-gamecube", 13),
	"virtualboy": Platform("virtualboy", "Nintendo Virtual Boy", "32-nintendo-virtual-boy", 11),
	"wii": Platform("wii", "Nintendo Wii", "33-nintendo-wii", 16),
	"wiiu": Platform("wiiu", "Nintendo Wii U", "34-nintendo-wii-u", 18),
	"switch": Platform("switch", "Nintendo Switch", "211-nintendo-switch", 225),
	"ouya": Platform("ouya", "Ouya", "35-ouya", 0),
	# 36 is skipped lol
	"cdi": Platform("cdi", "Philips CD-i", "37-philips-cd-i", 133),
	"pico8": Platform("pico8", "Pico-8", "220-pico-8", 234),
	"sega32x": Platform("sega32x", "Sega 32X", "38-sega-32x", 19),
	"segacd": Platform("segacd", "Sega CD", "39-sega-cd", 20),
	"dreamcast": Platform("dreamcast", "Sega Dreamcast", "40-sega-dreamcast", 23),
	"gamegear": Platform("gamegear", "Sega Game Gear", "41-sega-game-gear", 21),
	"genesis": Platform("genesis", "Sega Genesis", "42-sega-genesis", 1),
	"megadrive": Platform("megadrive", "Sega Mega Drive", "42-sega-genesis", 1),
	"mastersystem": Platform("mastersystem", "Sega Master System", "43-sega-master-system", 2),
	"naomi": Platform("naomi", "Sega NAOMI", "99-sega-naomi", 56),
	"naomi2": Platform("naomi2", "Sega NAOMI 2", "100-sega-naomi-2", 230),
	"saturn": Platform("saturn", "Sega Saturn", "45-sega-saturn", 22),
	"sg1000": Platform("sg1000", "Sega SG-1000", "80-sega-sg-1000", 109),
	"zxspectrum": Platform("zxspectrum", "Sinclair ZX Spectrum", "46-sinclair-zx-spectrum", 76),
	"psx": Platform("psx", "Sony Playstation", "47-sony-playstation", 57),
	"ps2": Platform("ps2", "Sony Playstation 2", "48-sony-playstation-2", 58),
	"ps3": Platform("ps3", "Sony Playstation 3", "49-sony-playstation-3", 59),
	"ps4": Platform("ps4", "Sony Playstation 4", "50-sony-playstation-4", 60),
	"ps5": Platform("ps5", "Sony Playstation 5", "219-sony-playstation-5", 0),
	"psvita": Platform("psvita", "Sony Playstation Vita", "51-sony-playstation-vita", 62),
	"psp": Platform("psp", "Sony Playstation Portable", "52-sony-psp", 61),
	"ti99": Platform("ti99", "Texas Instruments TI-99/4A", "149-texas-instruments-ti-994a", 205),
	"turbografx16": Platform("turbografx16", "NEC TurboGrafx-16", "54-nec-turbografx-16", 31),
	"turbografxcd": Platform("turbografxcd", "NEC TurboGrafx-CD", "163-nec-turbografx-cd", 0),
	"pcengine": Platform("pcengine", "NEC PC-Engine", "54-nec-turbografx-16", 31),
	"wonderswan": Platform("wonderswan", "WonderSwan", "55-wonderswan", 45),
	"wonderswancolor": Platform("wonderswancolor", "WonderSwan Color", "56-wonderswan-color", 46),
	"odyssey2": Platform("odyssey2", "Magnavox Odyssey 2", "57-magnavox-odyssey-2", 104),
	"odyssey": Platform("odyssey", "Magnavox Odyssey", "78-magnavox-odyssey", 0),
	"channelf": Platform("channelf", "Fairchild Channel F", "58-fairchild-channel-f", 80),
	"gamecom": Platform("gamecom", "Tiger Game.com", "63-tiger-gamecom", 121),
	"apple2": Platform("apple2", "Apple II", "111-apple-ii", 86),
}
