"""
Misc helper functions for clips2share
"""
import argparse
from importlib.resources import files


def format_tags_with_dots(source_list):
    return [s.replace(' ', '.') for s in source_list]

def print_torrent_hash_process(_, filepath, pieces_done, pieces_total):
    print(f'[{filepath}] {pieces_done / pieces_total * 100:3.0f} % done')

def get_font_path():
    return str(files('clips2share') / 'fonts')

def parse_arguments():
    parser = argparse.ArgumentParser(description="clips2share CLI")
    parser.add_argument('-V', '--video', type=str, help="Path to the video file")
    parser.add_argument('-u', '--url', type=str, help="Clip Store URL")
    parser.add_argument('-D', '--delay-seconds', type=int,
                        help="Auto-continue delay in seconds after torrent is created")
    return parser.parse_args()
