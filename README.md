# bsneo

bsneo is a rewrite of my older software [bigscraper-qt.](https://github.com/Fr75s/bigscraperqt) It aims to be a much cleaner implementation of what bigscraper-qt did, while also implementing some features which never made it to bigscraper-qt.

---

## New Features

### Multi-Platform

bsneo can be installed on not only Linux devices, but Windows devices as well. There are also plans to port bsneo to Android (though due to no official support coming until Python 3.13, this is not currently happening.)

### Parallel Scraping

bsneo enables you to run multiple scrapers at once. Each scraper runs parallel to another. There is no need to wait for one scraper to finish before another can run.

### Streamlined Interface

bsneo's interface, [made with flet,](https://flet.dev/) is less complex than bigscraper-qt while still containing every feature from it.

### Cleaner Backend

bsneo's cleaner backend comes from a complete rewrite of bigscraper-qt, making it more modular. This makes adding new scrapers & export formats much easier, allowing new features to come faster.

---

## Current Modules

The following Scrapers are currently available:

- [LaunchBox](https://gamesdb.launchbox-app.com/)

The following Export formats are also currently available:

- [Pegasus Frontend](https://pegasus-frontend.org/)

---

## Planned Features

The following changes to bsneo are planned for the future. Stay tuned.

- Android version
- ScreenScraper support
- File Management in app
