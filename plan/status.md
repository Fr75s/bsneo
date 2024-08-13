# STATUS

ALL STATUS CODES:

- idle: Idle
- hash: Process Hashes
- search: Downloading -> Scraping Search Page
- get: Downloading -> Scraping Game Page (LB: Includes getting image links (not downloading))
- image: Downloading Game Images
- video: Downloading Game Video
- finished: Finished

- error: An Error Occurred

OTHER STATUS DETAILS:

- scraped_count: The number of games that have been scraped

- game: The name of a game that was scraped
	- data: The metadata of the game that was scraped

STATUS FUNCTION:
{
	"new_code": STATUS CODE
	DETAIL: VALUE
}

## List Entry (Quick View)

- System
- # Games
- Quick Status (code -> description: PROGRESS/TOTAL)
- Quick Progress Bar (50% games_scraped/(ALL GAMES - games_failed), 50% games_success/(ALL GAMES - games_media_failed))

- Finish Check (color = SURFACE_TINT on new_code == finished)

## Screen

- System
- # Games

- Scraper Status
- Scraper Status Details

- List of Games Scraped
	- Game Metadata
	- Game Media + Download Status

- Search & Scrape Progress Bar
- All Media Downloaded Progress Bar

- Current Game: Current Media
- Current Media Download Progress Bar

