SCRAPING PROCESS

---

Steps

1. Get user input
2. Get info from filenames
3. Scrape Site
	A. Site is HTML (Launchbox)
		I. Fetch site
		II. Check if info is present
		III. If not, return to I with subsequent page or stop if end reached
		IV. If so, get info from content
		V. If media, download
	B. Site uses API
		I. Fetch with correct API params
		II. If no information, stop
		III. If information, get info from content
		IV. If media, download
4. Compile information into readable format
5. Compile media into reasonable place
6. Format information into usable metadata file
OPTIONAL: Customize Media
7. Copy metadata file and media to location
