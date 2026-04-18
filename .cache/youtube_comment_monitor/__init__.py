"""
YouTube Comment Monitor - Production-Ready Module
Fetches, categorizes, and responds to YouTube comments with full logging.
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Agent"

from .monitor import YouTubeCommentMonitor
from .categorizer import CommentCategorizer
from .responder import AutoResponder
from .logger import CommentLogger

__all__ = [
    'YouTubeCommentMonitor',
    'CommentCategorizer',
    'AutoResponder',
    'CommentLogger',
]
