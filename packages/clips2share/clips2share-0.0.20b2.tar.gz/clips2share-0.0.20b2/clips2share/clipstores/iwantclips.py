import re
from dataclasses import dataclass
from os import getenv
from typing import List

from bs4 import BeautifulSoup

from clips2share.clipstores.clipstore_interface import ClipstoreInterface, Clip
from clips2share.cloudscraper import cloudscraper  # TODO: import via pypi once updated there


@dataclass
class IWCClip(Clip):
    price: float
    description: str
    category: str
    nudity: str
    type: str
    length: str
    size: str
    resolution: str
    date: str
    keywords: List[str]


class Clipstore(ClipstoreInterface):
    supported_urls = ['www.iwantclips.com', 'iwantclips.com']

    @staticmethod
    def extract_clip_data(clip_url: str) -> IWCClip:
        """
        Extracts video data from HTML content and returns a IWCClip instance.
        """

        def _download_html_with_timeout(url: str, timeout: int = 10) -> str:
            """
            Downloads HTML page with cloudscraper including timeout handling.
            """
            # TODO: remove auto_refresh_on_403=False once upstream fixed refresh error
            scraper = cloudscraper.create_scraper(auto_refresh_on_403=False)
            try:
                response = scraper.get(url, timeout=timeout)
                response.raise_for_status()
                return response.text
            except Exception:
                return ""  # Empty string on error or timeout

        def _get_html_content(url: str, timeout: int = 10) -> str:
            """
            Attempts to download HTML page with cloudscraper. If not successful within timeout,
            prompts user for manual copy & paste input (unless running in CI environment).
            """
            print(f"Attempting to download HTML page from {url}...")
            html_content = _download_html_with_timeout(url, timeout)

            if html_content:
                return html_content

            print("Cloudscraper cloudflare bypass failed, this is an upstream Cloudscraper error, "
                  "not an issue with clips2share! ")

            # Check if running in CI environment
            if getenv('CI'):
                print("CI environment detected - skipping manual input.")
                return ""

            print("Please paste the HTML of the IWantclips Clip page manually via copy & paste.")
            print("End the input with a new line containing only 'EOF':")
            print("(Empty lines in HTML are allowed, only 'EOF' ends the input)")
            print("-" * 50)

            lines = []
            while True:
                try:
                    line = input()
                    if line.strip() == "EOF":
                        break
                    lines.append(line)
                except KeyboardInterrupt:
                    print("\nAborted.")
                    return ""
            return "\n".join(lines)

        soup = BeautifulSoup(_get_html_content(clip_url), 'html.parser')

        # Studio/Model Name
        studio_element = soup.select_one('.modelName .modelLink')
        studio = studio_element.get_text(strip=True) if studio_element else ""

        # Title
        title_element = soup.select_one('h1.no-style')
        title = title_element.get_text(strip=True) if title_element else ""

        # Price - Extract numerical value from USD price
        price_element = soup.select_one('.itemPrice span')
        price_text = price_element.get_text(strip=True) if price_element else ""
        price_match = re.search(r'\$\s*([\d.]+)', price_text)
        price = float(price_match.group(1)) if price_match else 0.0

        # Description - Robust extraction from various possible sources
        description = ""

        # disabled Meta-Description description (too short)

        # # 1. Try Meta-Description
        # meta_desc = soup.find('meta', {'name': 'description'})
        # if meta_desc and meta_desc.get('content'):
        #     description = meta_desc.get('content').strip()
        #
        # # 2. If Meta-Description not found, search in div.description
        # if not description:
        #     # Search for complete description (mobile version)
        #     desc_mobile = soup.select_one('.description.fix:not(.desktop-description) span')
        #     if desc_mobile:
        #         desc_text = desc_mobile.get_text(strip=True)
        #         if len(desc_text) > 20:  # Only if text is long enough
        #             description = desc_text

        # 3. If still empty, try desktop description + "more" text
        # this is probably the most complete
        if not description:
            desc_desktop = soup.select_one('.js-description')
            full_desc_hidden = soup.select_one('.js-full-description')

            if desc_desktop:
                description = full_desc_hidden.get_text(strip=True)
            elif full_desc_hidden:
                description = desc_desktop.get_text(strip=True)

        # 4. As last fallback: First .description with sufficient text
        if not description:
            all_descriptions = soup.select('.description span')
            for desc_elem in all_descriptions:
                text = desc_elem.get_text(strip=True)
                if len(text) > 20 and not text.lower().startswith('click for more'):
                    description = text
                    break
        # Category - Extract only the first category
        category = ""
        category_link = soup.select_one('.category')
        if category_link:
            category = category_link.get_text(strip=True).rstrip(',')

        # Thumbnail - Extract from og:image meta-tag or video poster
        thumbnail = ""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            thumbnail = og_image.get('content')
        else:
            # Fallback: Video poster attribute
            video_element = soup.find('video', {'poster': True})
            if video_element and video_element.get('poster'):
                thumbnail = video_element.get('poster')

        # Helper function for video properties
        def find_property_value(property_name: str) -> str:
            """Finds the value of a video property based on the property name."""
            rows = soup.find_all('div', class_='row')
            for row in rows:
                property_elem = row.find('span', class_='vidProperty')
                if property_elem and property_name.lower() in property_elem.get_text().lower():
                    value_elem = row.find('span', class_='vidPropertyValue')
                    if value_elem:
                        return value_elem.get_text(strip=True)
            return ""

        # Extract video properties
        nudity = find_property_value('nudity')
        video_type = find_property_value('media type')
        length = find_property_value('length')
        size = find_property_value('size')
        resolution_raw = find_property_value('resolution')
        date = find_property_value('published date')

        # Clean resolution (remove "HD " prefix)
        resolution = resolution_raw.replace('HD ', '') if resolution_raw.startswith(
            'HD ') else resolution_raw

        # Extract keywords
        keywords = []
        # Search for keywords text
        keywords_elements = soup.find_all(string=re.compile(r'Keywords:'))
        for keywords_elem in keywords_elements:
            parent = keywords_elem.parent
            text = parent.get_text()
            if 'Keywords:' in text:
                # Extract text after "Keywords:"
                keywords_text = text.split('Keywords:')[1].strip()
                # Split by comma and clean
                keywords_list = [kw.strip().rstrip(',').strip() for kw in keywords_text.split(',')]
                keywords = [kw for kw in keywords_list if kw and kw != '']
                break

        return IWCClip(
            studio=studio,
            title=title,
            price=price,
            description=description,
            category=category,
            nudity=nudity,
            type=video_type,
            length=length,
            size=size,
            resolution=resolution,
            date=date,
            keywords=keywords,
            image_url=thumbnail,
            url=clip_url
        )
