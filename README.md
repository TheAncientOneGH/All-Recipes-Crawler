# AllRecipes Crawler v1.0

A Python script using Selenium to crawl [www.allrecipes.com](https://www.allrecipes.com) and extract recipe data.

## Features

- Enjoy ad-free recipe browsing
- Extracts recipes from `www.allrecipes.com`
- Downloads a recipe image (250x250 or larger)
- Saves each recipe as an individual JSON file in `output/`
- Images saved to `output/images/`
- Automatic resume from last position if interrupted
- Skips already collected recipes
- Stop script via 'x' input or Ctrl+C
- Supports `--fullrun` flag to start from beginning
- `x` stops script (both crawler and viewer)
- `reload` reloads the database for the viewer

## Quick Start: (Windows)

- Clone or Download package and extract to a folder
- Double click `AllRecCrawler.cmd` to begin collecting recipes
- Double click `AllRecViewer.cmd` to view gathered recipes
- `AllRecViewer.cmd` can be launched while `AllRecCrawler.cmd` is running

## Installation

1. Install Python 3.8+
2. Install Chrome browser
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Normal Run (Resume Enabled)
```bash
python arc.py
```

The script will automatically resume from where it left off if previously interrupted.

### Full Run (Start from Beginning)
```bash
python arc.py --fullrun
```

Ignores saved progress and starts fresh from the homepage.

## After Gathering Some Recipes
```bash
python arv.py
```

Allows viewing recipes in an HTML layout.

## Directory Structure

```
AllRecipes/
├── .allrec/*                   # Python Virtual Environment (Automatically Created)
├── output/*                    # Collected Recipes and Data (Automatically Created)
├── python/*                    # Embedded Python v3.14.0
├── skip/                       # Directory to store skip word/url definitions
│   ├── ignore.json             # Word based ignore list
│   └── skiplist.json           # URL based ignore list
├── templates/                  # Directory containing templates for viewer front end
│   ├── index.html              # Main HTML template for viewing recipes
│   ├── noimage.jpg             # Fallback image incase no recipe image found
│   └── noodles.png             # Favicon used in index.html
├── screenshots/*               # Screenshots of Crawler and Viewer
├── arc.py                      # Main crawler script
├── arv.py                      # Main viewer script
├── requirements.txt            # Minimum python dependencies
├── AllRecCrawler.cmd           # Quick start crawler batch command
├── AllRecViewer.cmd            # Quick start viewer batch command
├── LICENSE.md                  # License Information
├── README.md                   # This file
├── error.log                   # Errors get written here (at least most of them - Automatically Created)
├── arc.lock                    # Prevent running multiple instance crawler (Automatically Created)
└── arv.lock                    # Prevent running multiple instance viewer (Automatically Created)
```

### Stopping the Crawler

- Type `x` and press Enter to stop gracefully
- Press Ctrl+C to stop (handled gracefully)
- Progress is automatically saved on shutdown

## Output Format

Each recipe JSON file contains (Just as example):
```json
{
  "name": "1-2-3-4_Recipe_Name",
  "origin": [
    "American",
    "German",
    "..."
  ],
  "category": [
    "Dessert",
    "Dinner",
    "Cake"
  ],
  "ingredients": [
    "1 Cup Salted Butter",
    "1 tsp. Sugar",
    "..."
  ],
  "instructions": [
    "Step 1 ...",
    "Step 2 ...",
    "..."
  ],
  "href": "https://",
  "site": "www.allrecipes.com",
  "url": "https://www.allrecipes.com/1-2-3-4-Recipe_Name",
  "image": true,
  "v": "1.0",
  "extracted_at": "2026-05-10T18:36:06.379697"
}
```

## Notes

- Only recipes with valid structured data are collected
- Images are filtered to accept a minimum of 250x250 pixels
- Special characters are removed from filenames
- Already collected recipes are automatically skipped on resume
- Use `--fullrun` to start checking links from beginning of crawl (Will not lose already gathered)
- Use `get:<url>` to manually add a recipe link (ex. get:https://somelink.com/recipe/)
- If you need to rebuild your database file, simply delete the old one `output/db/allrec.db`
  then run Crawler again and it will rebuild the file contents.
- Database rebuilding does require the JSON files in `output/`

## To-Do

- Possibly other features as time allows

## License

- Attribution-NonCommercial-NoDerivatives 4.0 International
- For educational purposes only. Respect AllRecipes terms of service.

## Donate

[Donate via Paypal](https://www.paypal.com/donate/?hosted_button_id=JJ2KF3GDK9C38)

## Screenshots

![Crawler](screenshots/crawler.png)

![Viewer Console](screenshots/viewerconsole.png)

![Viewer GUI](screenshots/viewergui.png)
