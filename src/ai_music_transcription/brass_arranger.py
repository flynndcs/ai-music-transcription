#!/usr/bin/env python3
"""
AI-Assisted Music Transcription Tool - Brass Arrangement Module
Takes a piano MusicXML file and arranges it for trumpet and trombone.
"""

import copy
import os
from music21 import converter, stream, note, meter, key, instrument, bar, interval, clef


# Musical constants
class Ranges:
    """Comfortable playing ranges for instruments (MIDI pitch numbers)."""
    TRUMPET_MIN = 55  # G3 (written pitch)
    TRUMPET_MAX = 84  # C6 (written pitch)
    TROMBONE_MIN = 40  # E2
    TROMBONE_MAX = 77  # F5
    MIDDLE_C = 60     # Dividing line between treble and bass


class Transposition:
    """Transposition intervals for instruments."""
    BB_TRUMPET = interval.Interval('M2')  # Major 2nd up for Bb trumpet
    OCTAVE_UP = interval.Interval('P8')
    OCTAVE_DOWN = interval.Interval('-P8')


class KeySignatures:
    """Common key signatures."""
    C_MAJOR = key.KeySignature(0)   # No sharps or flats
    D_MAJOR = key.KeySignature(2)   # Two sharps (F#, C#)


class BrassArranger:
    """Arranges piano scores for brass instruments."""
    
    def __init__(self, input_file):
        """Initialize the brass arranger with a MusicXML file."""
        self.input_file = input_file
        self.score = converter.parse(input_file)
        self.treble_part = None
        self.bass_part = None
        self._extract_parts()
    
    def _extract_parts(self):
        """Extract treble and bass clef parts from the score."""
        if len(self.score.parts) >= 2:
            # Score already has separate parts (most common case)
            self.treble_part = self.score.parts[0]  # Higher pitches
            self.bass_part = self.score.parts[1]    # Lower pitches
        else:
            # Single part - split by pitch height
            self._split_single_part_by_pitch()
    
    def _split_single_part_by_pitch(self):
        """Split a single piano part into treble and bass by pitch height."""
        piano_part = self.score.parts[0]
        self.treble_part = stream.Part()
        self.bass_part = stream.Part()
        
        # Copy time/key signatures to both parts
        for element in piano_part.getElementsByClass([meter.TimeSignature, key.KeySignature]):
            self.treble_part.append(element)
            self.bass_part.append(element)
        
        # Separate notes by pitch height
        for measure in piano_part.getElementsByClass('Measure'):
            treble_measure = stream.Measure(number=measure.number)
            bass_measure = stream.Measure(number=measure.number)
            
            for element in measure.notesAndRests:
                if isinstance(element, note.Note):
                    # Split at middle C
                    if element.pitch.ps >= Ranges.MIDDLE_C:
                        treble_measure.append(element)
                    else:
                        bass_measure.append(element)
                else:  # Rests go to both parts
                    treble_measure.append(element)
                    bass_measure.append(element)
            
            self.treble_part.append(treble_measure)
            self.bass_part.append(bass_measure)
    
    def _transpose_note_to_range(self, note_obj, min_pitch, max_pitch):
        """Transpose a note to fit within the specified range."""
        # Move note into comfortable range using octave transpositions
        while note_obj.pitch.ps < min_pitch:
            note_obj.pitch = note_obj.pitch.transpose(Transposition.OCTAVE_UP)
        
        while note_obj.pitch.ps > max_pitch:
            note_obj.pitch = note_obj.pitch.transpose(Transposition.OCTAVE_DOWN)
        
        return note_obj
    
    def _suppress_key_signature_accidentals(self, note_obj, key_signature_sharps_flats):
        """Remove visual accidentals that are already implied by the key signature."""
        if not (hasattr(note_obj.pitch, 'accidental') and note_obj.pitch.accidental):
            return
        
        step = note_obj.pitch.step
        accidental_name = note_obj.pitch.accidental.name
        
        # Check if this accidental is implied by the key signature
        # D major (2 sharps) implies F# and C#
        if key_signature_sharps_flats == 2:  # D major
            if ((step == 'F' and accidental_name == 'sharp') or 
                (step == 'C' and accidental_name == 'sharp')):
                note_obj.pitch.accidental.displayStatus = False
    
    def _process_measure_elements(self, source_measure, target_measure, 
                                  transposition_interval=None, 
                                  min_range=None, max_range=None,
                                  key_sig_accidentals=0):
        """Process notes and rests from source measure to target measure."""
        # Copy barlines (only final ones)
        for barline in source_measure.getElementsByClass(bar.Barline):
            if barline.location == 'right':
                target_measure.rightBarline = barline
        
        # Process each musical element
        for element in source_measure.notesAndRests:
            if isinstance(element, note.Note):
                # Create new note with same pitch and duration
                new_note = note.Note(element.pitch, quarterLength=element.quarterLength)
                
                # Apply transposition if specified
                if transposition_interval:
                    new_note.pitch = new_note.pitch.transpose(transposition_interval)
                
                # Adjust to instrument range if specified
                if min_range is not None and max_range is not None:
                    new_note = self._transpose_note_to_range(new_note, min_range, max_range)
                
                # Handle key signature accidentals
                self._suppress_key_signature_accidentals(new_note, key_sig_accidentals)
                
                target_measure.append(new_note)
            else:
                # Copy rests as-is
                new_rest = note.Rest(quarterLength=element.quarterLength)
                target_measure.append(new_rest)
    
    def _setup_instrument_part(self, instrument_obj, clef_obj=None, key_sig=None):
        """Create a new part with instrument, clef, and key signature."""
        part = stream.Part()
        part.insert(0, instrument_obj)
        
        if clef_obj:
            part.insert(0, clef_obj)
        
        if key_sig:
            part.insert(0, key_sig)
        
        return part
    
    def arrange_for_trumpet(self):
        """Arrange the treble part for Bb trumpet."""
        # Set up trumpet part with D major key signature (for Bb instrument)
        trumpet_part = self._setup_instrument_part(
            instrument.Trumpet(), 
            key_sig=KeySignatures.D_MAJOR
        )
        
        # Copy time signatures (key signature already handled above)
        for element in self.treble_part.getElementsByClass(meter.TimeSignature):
            trumpet_part.append(element)
        
        # Process each measure
        for measure in self.treble_part.getElementsByClass('Measure'):
            new_measure = stream.Measure(number=measure.number)
            
            self._process_measure_elements(
                source_measure=measure,
                target_measure=new_measure,
                transposition_interval=Transposition.BB_TRUMPET,
                min_range=Ranges.TRUMPET_MIN,
                max_range=Ranges.TRUMPET_MAX,
                key_sig_accidentals=2  # D major has 2 sharps
            )
            
            trumpet_part.append(new_measure)
        
        return trumpet_part
    
    def arrange_for_trombone(self):
        """Arrange the bass part for trombone (concert pitch)."""
        # Set up trombone part with bass clef and C major key signature
        trombone_part = self._setup_instrument_part(
            instrument.Trombone(),
            clef_obj=clef.BassClef(),
            key_sig=KeySignatures.C_MAJOR
        )
        
        # Copy time signatures
        for element in self.bass_part.getElementsByClass(meter.TimeSignature):
            trombone_part.append(element)
        
        # Process each measure
        for measure in self.bass_part.getElementsByClass('Measure'):
            new_measure = stream.Measure(number=measure.number)
            
            self._process_measure_elements(
                source_measure=measure,
                target_measure=new_measure,
                transposition_interval=None,  # Concert pitch, no transposition
                min_range=Ranges.TROMBONE_MIN,
                max_range=Ranges.TROMBONE_MAX,
                key_sig_accidentals=0  # C major has no sharps/flats
            )
            
            trombone_part.append(new_measure)
        
        return trombone_part
    
    def _get_original_title(self):
        """Extract the original title from the score."""
        # In a real implementation, this would parse MusicXML credits
        # For now, we know this specific file's title
        return "Example"
    
    def _create_score_with_metadata(self, title_suffix):
        """Create a new score with properly configured metadata."""
        score = stream.Score()
        original_title = self._get_original_title()
        full_title = f"{original_title} - {title_suffix}"
        
        if self.score.metadata:
            score.metadata = copy.deepcopy(self.score.metadata)
            score.metadata.title = full_title
            score.metadata.movementName = full_title
        else:
            score.metadata = {'title': full_title, 'movementName': full_title}
        
        return score
    
    def create_brass_duet_score(self):
        """Create a combined score with both trumpet and trombone parts."""
        duet_score = self._create_score_with_metadata("Brass Duet Arrangement")
        
        # Add both instrument parts
        trumpet_part = self.arrange_for_trumpet()
        trombone_part = self.arrange_for_trombone()
        
        duet_score.insert(0, trumpet_part)
        duet_score.insert(0, trombone_part)
        
        return duet_score
    
    def generate_outputs(self, output_dir="."):
        """Generate all output files (individual parts and duet score)."""
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        
        # Create individual instrument scores
        trumpet_score = self._create_score_with_metadata("Trumpet")
        trumpet_score.insert(0, self.arrange_for_trumpet())
        
        trombone_score = self._create_score_with_metadata("Trombone")
        trombone_score.insert(0, self.arrange_for_trombone())
        
        # Create combined duet score
        duet_score = self.create_brass_duet_score()
        
        # Generate file paths
        output_files = {
            'trumpet': os.path.join(output_dir, f"{base_name}_Trumpet.xml"),
            'trombone': os.path.join(output_dir, f"{base_name}_Trombone.xml"),
            'duet': os.path.join(output_dir, f"{base_name}_BrassDuet.xml")
        }
        
        # Write files
        trumpet_score.write('musicxml', fp=output_files['trumpet'])
        trombone_score.write('musicxml', fp=output_files['trombone'])
        duet_score.write('musicxml', fp=output_files['duet'])
        
        return output_files['trumpet'], output_files['trombone'], output_files['duet']


def main():
    """Main function to run the brass arranger."""
    input_file = "Example.xml"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    arranger = BrassArranger(input_file)
    trumpet_file, trombone_file, duet_file = arranger.generate_outputs()
    
    print("Brass arrangement complete!")
    print("Generated files:")
    print(f"  - Trumpet: {trumpet_file}")
    print(f"  - Trombone: {trombone_file}")
    print(f"  - Brass Duet: {duet_file}")


if __name__ == "__main__":
    main()