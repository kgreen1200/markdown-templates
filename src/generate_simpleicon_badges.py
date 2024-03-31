import json
import shutil
import string
from pathlib import Path

import requests
import pandas as pd
from slugify import slugify
from unidecode import unidecode

ICONS_URL = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/_data/simple-icons.json"
BRIGHTNESS_THRESHOLD = 0.69  # https://github.com/badges/shields/blob/master/badge-maker/lib/badge-renderers.js#L20
DOCS_DIR = Path("docs/badges")

def brightness(h):
    """
    Python conversion of https://github.com/badges/shields/blob/master/badge-maker/lib/color.js#L71
    """
    h = h.lstrip("#")
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 255000

# Clear out docs directory for storing badge titles
if DOCS_DIR.is_dir():
    shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True)

# Generate default badge files
files = list(string.ascii_lowercase) + ["#"]
for c in files:
    file = DOCS_DIR / f"badges_{c}.md"
    if not file.is_file():
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open(mode="w", encoding="utf8") as badge_list:
            title = "\#" if c == "#" else c
            badge_list.write(f"# Generated Brand Shields - {title.upper()}\n| Name | Badge | URL | Brand Guidelines |\n| ---: | :---: | :--- | :--- |\n")

# Get list of icons from SimpleIcons
slugs_df = pd.DataFrame(json.loads(unidecode(requests.get(ICONS_URL, timeout=60).text))["icons"])
slugs_df = slugs_df.set_index("title")

# Import data and write to Markdown
for index, data in slugs_df.iterrows():
    names, slug, h, guidelines, aliases = [index], data["slug"], data["hex"], data["guidelines"], data["aliases"]

    slug = slugify(index.replace(".", "dot").replace("#", "sharp"), separator="") if pd.isnull(slug) else slug
    guidelines = f"[Link]({guidelines})" if not pd.isnull(guidelines) else " "
    text_color = "FFFFFF" if brightness(h) <= BRIGHTNESS_THRESHOLD  else "333333"

    if not pd.isnull(aliases):
        if "aka" in aliases:
            names = names + aliases["aka"]
        if "old" in aliases:
            names = names + aliases["old"]

    if index[0].isdigit() or index[0] in string.punctuation:
        file_index = "#"
    else:
        file_index = index[0].lower()
    file = DOCS_DIR / f"badges_{file_index}.md"
    with file.open("a", encoding="utf8") as badge_list:
        for name in names:
            formatted_name = name.replace(" ", "_").replace("-", "--")
            badge_url = f"https://img.shields.io/badge/{formatted_name}-{h}?style=for-the-badge&logo={slug}&logoColor={text_color}"
            badge_list.write(f"| {index} | ![{name}]({badge_url}) | `{badge_url}` | {guidelines} |\n")