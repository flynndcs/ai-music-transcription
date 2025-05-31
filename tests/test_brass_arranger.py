#!/usr/bin/env python3
"""
Unit tests for the BrassArranger class.

Run with: python -m pytest tests/
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

from ai_music_transcription import BrassArranger


class TestBrassArranger(unittest.TestCase):
    """Test cases for BrassArranger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.example_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "examples", 
            "Example.xml"
        )
    
    def test_initialization(self):
        """Test BrassArranger initialization."""
        if os.path.exists(self.example_file):
            arranger = BrassArranger(self.example_file)
            self.assertIsNotNone(arranger.score)
            self.assertIsNotNone(arranger.treble_part)
            self.assertIsNotNone(arranger.bass_part)
    
    def test_title_extraction(self):
        """Test original title extraction."""
        if os.path.exists(self.example_file):
            arranger = BrassArranger(self.example_file)
            title = arranger._get_original_title()
            self.assertEqual(title, "Example")
    
    def test_output_generation(self):
        """Test that output files are generated correctly."""
        if os.path.exists(self.example_file):
            with tempfile.TemporaryDirectory() as temp_dir:
                arranger = BrassArranger(self.example_file)
                trumpet_file, trombone_file, duet_file = arranger.generate_outputs(temp_dir)
                
                # Check that files were created
                self.assertTrue(os.path.exists(trumpet_file))
                self.assertTrue(os.path.exists(trombone_file))
                self.assertTrue(os.path.exists(duet_file))
                
                # Check file sizes are reasonable (not empty)
                self.assertGreater(os.path.getsize(trumpet_file), 1000)
                self.assertGreater(os.path.getsize(trombone_file), 1000)
                self.assertGreater(os.path.getsize(duet_file), 2000)
    
    def test_ranges_constants(self):
        """Test that range constants are reasonable."""
        from ai_music_transcription.brass_arranger import Ranges
        
        # Test that ranges make musical sense
        self.assertLess(Ranges.TRUMPET_MIN, Ranges.TRUMPET_MAX)
        self.assertLess(Ranges.TROMBONE_MIN, Ranges.TROMBONE_MAX)
        
        # Test that middle C is reasonable
        self.assertEqual(Ranges.MIDDLE_C, 60)  # MIDI note 60 = Middle C
    
    def test_transposition_constants(self):
        """Test that transposition intervals are correct."""
        from ai_music_transcription.brass_arranger import Transposition
        
        # Test Bb trumpet transposition (should be major 2nd)
        interval = Transposition.BB_TRUMPET
        self.assertEqual(interval.semitones, 2)  # Major 2nd = 2 semitones
    
    @unittest.skipIf(not os.path.exists(os.path.join(os.path.dirname(__file__), "..", "examples", "Example.xml")), 
                     "Example.xml not found")
    def test_full_workflow(self):
        """Test the complete arrangement workflow."""
        arranger = BrassArranger(self.example_file)
        
        # Test individual arrangements
        trumpet_part = arranger.arrange_for_trumpet()
        trombone_part = arranger.arrange_for_trombone()
        
        self.assertIsNotNone(trumpet_part)
        self.assertIsNotNone(trombone_part)
        
        # Test combined score
        duet_score = arranger.create_brass_duet_score()
        self.assertIsNotNone(duet_score)
        self.assertEqual(len(duet_score.parts), 2)


if __name__ == "__main__":
    unittest.main()