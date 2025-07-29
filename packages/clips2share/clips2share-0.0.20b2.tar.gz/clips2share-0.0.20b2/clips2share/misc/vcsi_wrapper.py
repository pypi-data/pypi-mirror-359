"""
Helper for accessing standalone vsci library
"""

import argparse

from vcsi import vcsi

from clips2share.misc.functions import get_font_path

# Create namespace for non interactive vcsi run
# (using default vcsi parameters copied from interactive debug run)
# output_path needs to be defined from outside:
# vcsi_args.output_path=target_dir + '/images/thumbnail.jpg'
vcsi_args = argparse.Namespace(config=None,
                               start_delay_percent=7,
                               end_delay_percent=7, delay_percent=None, grid_spacing=None,
                               grid_horizontal_spacing=5,
                               grid_vertical_spacing=5, vcs_width=1500,
                               grid=vcsi.Grid(x=4, y=4), num_samples=None,
                               show_timestamp=True, metadata_font_size=16,
                               metadata_font=get_font_path() + '/DejaVuSans-Bold.ttf',
                               timestamp_font_size=12,
                               timestamp_font=get_font_path() + '/DejaVuSans.ttf',
                               metadata_position='top',
                               background_color=vcsi.Color(r=0, g=0, b=0, a=255),
                               metadata_font_color=vcsi.Color(r=255, g=255, b=255, a=255),
                               timestamp_font_color=vcsi.Color(r=255, g=255, b=255, a=255),
                               timestamp_background_color=vcsi.Color(r=0, g=0, b=0, a=170),
                               timestamp_border_color=vcsi.Color(r=0, g=0, b=0, a=255),
                               metadata_template_path=None,
                               manual_timestamps=None, is_verbose=False, is_accurate=False,
                               accurate_delay_seconds=1,
                               metadata_margin=10, metadata_horizontal_margin=10,
                               metadata_vertical_margin=10,
                               timestamp_horizontal_padding=3, timestamp_vertical_padding=3,
                               timestamp_horizontal_margin=5, timestamp_vertical_margin=5,
                               image_quality=100,
                               image_format='jpg', recursive=False, timestamp_border_mode=False,
                               timestamp_border_size=1,
                               capture_alpha=255, list_template_attributes=False,
                               frame_type=None, interval=None,
                               ignore_errors=False, no_overwrite=False, exclude_extensions=[],
                               fast=False,
                               thumbnail_output_path=None, actual_size=False,
                               timestamp_format='{TIME}',
                               timestamp_position=vcsi.TimestampPosition.se
)
