"""
AI-Assisted Music Transcription Tool

A Python library for converting piano scores to brass instrument arrangements.
Currently supports trumpet and trombone arrangements with proper transposition,
key signatures, and musical notation conventions.
"""

from .brass_arranger import BrassArranger

__version__ = "0.1.0"
__author__ = "AI Music Transcription Team"
__all__ = ["BrassArranger"]