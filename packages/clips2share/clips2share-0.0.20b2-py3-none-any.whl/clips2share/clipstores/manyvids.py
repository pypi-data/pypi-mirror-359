import re
from dataclasses import dataclass

import requests

from clips2share.clipstores.clipstore_interface import ClipstoreInterface, Clip


@dataclass
class MVClip(Clip):
    price: str
    date: str
    duration: str
    size: str
    extension: str
    resolution: str
    description: str
    keywords: list[str]


class Clipstore(ClipstoreInterface):
    supported_urls = ['www.manyvids.com', 'manyvids.com']

    @staticmethod
    def extract_clip_data(clip_url: str) -> MVClip:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        }

        def extract_clip_id(url):
            # https://www.manyvids.com/Video/12345/my-video
            return re.search(r'/Video/(\d+)', url).group(1)

        response = requests.get(f'https://api.manyvids.com/store/video/{extract_clip_id(clip_url)}',
                                timeout=10,
                                headers=headers
                                )

        response.raise_for_status()
        clip = response.json()
        if clip['statusCode'] != 200 or clip['statusMessage'] != 'OK':
            raise ValueError(f'Invalid json data returned: {clip}')

        title = clip['data']['title']
        studio = clip['data']['model']['displayName']
        price = clip['data']['price']['regular']
        date = clip['data']['launchDate'][:10]
        duration = clip['data']['videoDuration']
        size = clip['data']['size'].replace(' MB', '')
        extension = clip['data']['extension']
        resolution = clip['data']['width']
        description = clip['data'].get('description')
        # category missing
        keywords = []

        if 'tagList' in clip['data']:
            keywords = [tag['label'] for tag in clip['data']['tagList']]

        image_url = clip['data']['screenshot']

        return MVClip(
            title=title,
            studio=studio,
            price=price,
            date=date,
            duration=duration,
            size=size,
            extension=extension,
            resolution=resolution,
            description=description,
            keywords=keywords,
            url=clip_url,
            image_url=image_url
        )
