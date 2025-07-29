import json
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests

from clips2share.clipstores.clipstore_interface import ClipstoreInterface, Clip


def html2text(html):
    f = HTMLFilter()
    f.feed(html)
    return f.text


class HTMLFilter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ''

    def handle_data(self, data):
        self.text += data

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.text += '\n'
        if tag == 'p':
            self.text += '\n'


@dataclass
class C4SClip(Clip):
    price: str
    date: str
    duration: str
    size: str
    extension: str
    resolution: str
    description: str
    category: str
    related_categories: list[str]
    keywords: list[str]


class Clipstore(ClipstoreInterface):
    supported_urls = ['clips4sale.com', 'www.clips4sale.com']

    @staticmethod
    def extract_clip_data(clip_url: str) -> C4SClip:
        decoder = json.JSONDecoder()

        api_url = urljoin(clip_url,
                          '?_data=routes%2F%28%24lang%29.studio.%24id_.%24clipId.%24clipSlug')
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        obj, _ = decoder.raw_decode(response.text)
        clip = obj['clip']
        title = clip['title']
        studio = clip['studioTitle']
        price = clip['price']
        date = clip['dateDisplay'].split(' ')[0]  # no split would also give you the timestamp
        duration = clip['duration']
        size = clip['size_mb']
        extension = clip['format']
        resolution = clip['resolution']
        description = html2text(clip['description_sanitized'])
        category = clip['category_name']
        related_categories = []
        keywords = []

        if 'related_category_links' in clip:
            related_category_links = clip['related_category_links']
            related_categories = [category['category'] for category in related_category_links]

        if 'keyword_links' in clip:
            keyword_links = clip['keyword_links']
            keywords = [keyword['keyword'] for keyword in keyword_links]

        image_url = clip['cdn_previewlg_link']

        return C4SClip(
            title=title,
            studio=studio,
            price=price,
            date=date,
            duration=duration,
            size=size,
            extension=extension,
            resolution=resolution,
            description=html2text(description),
            category=category,
            related_categories=related_categories,
            keywords=keywords,
            url=clip_url,
            image_url=image_url
        )
