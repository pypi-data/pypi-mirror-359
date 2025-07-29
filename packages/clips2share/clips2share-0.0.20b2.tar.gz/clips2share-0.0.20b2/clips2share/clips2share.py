import sys
import time
import tomllib
from os import getenv, makedirs, remove, symlink, link
from os.path import abspath, dirname, isfile, splitext
from pathlib import Path
from shutil import move
from urllib.parse import urlparse

import requests
from jinja2 import Environment, FileSystemLoader
from platformdirs import user_config_dir
from torf import Torrent
from vcsi import vcsi

# Support for direct script execution
# This is a workaround for running the script directly without installing it as a package.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, abspath(dirname(__file__) + "/.."))

# pylint: disable=wrong-import-position
# we need to fix the above workaround first to fix import order
from clips2share.clients import qbittorrent
from clips2share.clipstores import clips4sale, iwantclips, manyvids
from clips2share.imagehoster.chevereto import chevereto_image_upload
from clips2share.misc.models import Tracker
from clips2share.misc.functions import (format_tags_with_dots,
                                        print_torrent_hash_process,
                                        parse_arguments)
from clips2share.misc.vcsi_wrapper import vcsi_args


def main():
    args = parse_arguments()
    config_path = getenv('C2S_CONFIG_PATH') if getenv('C2S_CONFIG_PATH') else user_config_dir(
        appname='clips2share') + '/config.toml'
    if not isfile(config_path):
        print(f'config_path {config_path} does not exist, download example config here: '
              f'https://codeberg.org/c2s/clips2share/src/branch/main/config.toml.example '
              f'change to your needs and run again!'
        )
        sys.exit(1)
    with open(config_path, 'rb') as f:
        toml_data = tomllib.load(f)

    torrent_temp_dir = toml_data['torrent']['temporary_directory']
    upload_dir = toml_data['client']['qbittorrent']['upload_directory']
    qbittorrent_watch_dir = toml_data['client']['qbittorrent']['watch_directory']
    static_tags = toml_data['torrent']['static_tags']
    delayed_seed = toml_data['client']['qbittorrent']['delayed_seed']
    use_hardlinks = toml_data['torrent'].get('use_hardlinks', False)
    torrent_description_template = toml_data['torrent'].get('template', 'default_bbcode.jinja')

    chevereto_api_key = toml_data['image_host']['chevereto']['api_key']
    chevereto_host = toml_data['image_host']['chevereto']['host']

    use_qb_api = toml_data['client']['qbittorrent']['use_api']
    qb_url = toml_data['client']['qbittorrent']['url']
    qb_category = toml_data['client']['qbittorrent']['category']

    if use_qb_api:
        qbt_client = qbittorrent.QBittorrentClient(qb_url)

    trackers = [Tracker(**t) for t in toml_data.get('trackers', [])]
    print(trackers)

    video_path = args.video if args.video else input("Video Path: ")
    clip_url = args.url if args.url else input("Clip Url: ")

    if not isfile(video_path):
        print('Video file does not exists: ', video_path)
        sys.exit(2)

    clipstores = [clips4sale, iwantclips, manyvids]

    clip = None
    domain = urlparse(clip_url).netloc

    for clipstore in clipstores:
        if domain in clipstore.Clipstore.supported_urls:
            clip = clipstore.Clipstore.extract_clip_data(clip_url)
            print(clip)
            break
    else:
        raise NotImplementedError(f'Clipstore {domain} is not implemented')


    target_dir = upload_dir + f'{clip.studio} - {clip.title}'

    # Create dir structure
    makedirs(target_dir + '/images')

    target_file_path = f'{target_dir}/{clip.studio} - {clip.title}{splitext(video_path)[1]}'

    # Create hardlink or symlink to video file in upload dir
    if use_hardlinks:
        print(f"Creating hardlink: {target_file_path}")
        link(src=video_path, dst=target_file_path)
    else:
        print(f"Creating symlink: {target_file_path}")
        symlink(src=video_path, dst=target_file_path)

    # Download Header Image
    r = requests.get(clip.image_url, timeout=10)
    r.raise_for_status()
    with open(target_dir + '/images/header.jpg', 'wb') as header:
        header.write(r.content)

    # Upload header image
    header_image_link = chevereto_image_upload(target_dir + '/images/header.jpg',
                                               chevereto_host=chevereto_host,
                                               chevereto_api_key=chevereto_api_key
    )

    vcsi_args.output_path=target_dir + '/images/thumbnail.jpg'
    vcsi.process_file(f'{target_dir}/{clip.studio} - {clip.title}{splitext(video_path)[1]}',
                      args=vcsi_args
    )

    thumbnail_image_link = chevereto_image_upload(target_dir + '/images/thumbnail.jpg',
                                                  chevereto_host=chevereto_host,
                                                  chevereto_api_key=chevereto_api_key
    )

    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir / 'templates'

    jinja_env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True
    )

    t = Torrent(path=target_dir)
    t.private = True
    # pylint: disable=protected-access
    t._metainfo['metadata'] = {}
    t._metainfo['metadata']['title'] = f'{clip.studio} - {clip.title}'
    t._metainfo['metadata']['cover url'] = header_image_link
    t._metainfo['metadata']['taglist'] = format_tags_with_dots(clip.keywords + static_tags)
    template = jinja_env.get_template(torrent_description_template)
    t._metainfo['metadata']['description'] = template.render(
        clip=clip,
        header_image_link=header_image_link,
        thumbnail_image_link=thumbnail_image_link,
    )
    print("BBCode:\n"
          "-----TORRENT DESCRIPTION-----\n" +
          t._metainfo['metadata']['description'] +
          "\n-----DESCRIPTION END-----\n"
    )

    t.generate(callback=print_torrent_hash_process, interval=1)

    # Create Torrents
    for tracker in trackers:
        t.trackers = tracker.announce_url
        t.source = tracker.source_tag

        # TODO: category is not working, this is probably unsupported on luminance currently?
        t._metainfo['metadata']['category'] = tracker.category

        print(f'creating torrent for {tracker.source_tag}... {t}')

        t.write(f'{torrent_temp_dir}[{tracker.source_tag}]{clip.studio} - {clip.title}.torrent')
        if delayed_seed:
            if args.delay_seconds:
                print(
                    f'Upload torrent to tracker {tracker.source_tag}.'
                    f'Waiting {args.delay_seconds} seconds before autoloading to qBittorrent...'
                )
                time.sleep(args.delay_seconds)
            else:
                input(
                    f'Upload torrent to tracker {tracker.source_tag},'
                    f'then hit Enter to autoload to qBittorrent...'
                )

        torrent_filename = f'[{tracker.source_tag}]{clip.studio} - {clip.title}.torrent'
        torrent_path = f'{torrent_temp_dir}{torrent_filename}'

        if use_qb_api:
            print(f"Uploading {torrent_filename} via qBittorrent API...")
            torrent_name = f'{clip.studio} - {clip.title}'
            try:
                with open(torrent_path, 'rb') as f:
                    torrent_bytes = f.read()
                qbt_client.send_torrent(
                    torrent_bytes=torrent_bytes,
                    name=torrent_name,
                    category=qb_category,
                    savepath=upload_dir,
                )
                print("API Upload successful.")
                # Clean up the temporary torrent file after successful upload
                try:
                    remove(torrent_path)
                except OSError as e:
                    print(f"Error removing temp torrent {torrent_path}: {e}")
            except Exception as e:
                print("API upload failed:", e)
                sys.exit(3)
        else:
            watch_target = f'{qbittorrent_watch_dir}{torrent_filename}'
            print(f"Using watch folder: {watch_target}")
            move(torrent_path, watch_target)

        t.trackers.clear()
        t.source = None
        print('done...')


if __name__ == "__main__":
    main()
