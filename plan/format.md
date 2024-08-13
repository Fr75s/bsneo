Required Fields:

- "filename" [1: filepath]
- "name" [1: str]
- "clean_name" [1: str]
- "platform" [1: str (pid)]

- "scraped_with" [1+: str]

Optional Fields:

- "imgs" [1+: dict[str, filepath]]
	- "assetType" : "filepath"
- "video" [1: str] OR "videourl" [1: url]
- "desc" [1: str]
- "release" [1: isodate]
- "developers" [1+: str]
- "publishers" [1+: str]
- "genres" [1+: str]
- "rating" [1: float]
