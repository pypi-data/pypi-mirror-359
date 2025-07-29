"""
Shared dataclasses from clips2share
"""

from dataclasses import dataclass

@dataclass
class Tracker:
    name: str
    announce_url: str
    category: str
    source_tag: str
