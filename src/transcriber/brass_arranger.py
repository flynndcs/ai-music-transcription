#!/usr/bin/env python3
"""
Transcriber - Brass Arrangement Module
Takes a piano MusicXML file and arranges it for trumpet and trombone.
"""

import copy
import os
import tempfile
import librosa
import soundfile as sf
import numpy as np
from music21 import converter, stream, note, meter, key, instrument, bar, interval, clef, pitch


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
    """Key signature utilities."""
    @staticmethod
    def transpose_key_signature(original_key, transposition_interval):
        """Transpose a key signature by the given interval."""
        if original_key.sharps == 0:  # C major
            if transposition_interval.name == 'M2':  # Major 2nd up
                return key.KeySignature(2)  # D major
            elif transposition_interval.name == 'P5':  # Perfect 5th up
                return key.KeySignature(1)  # G major
        elif original_key.sharps == 1:  # G major
            if transposition_interval.name == 'M2':  # Major 2nd up
                return key.KeySignature(3)  # A major
        elif original_key.sharps == 2:  # D major
            if transposition_interval.name == 'M2':  # Major 2nd up
                return key.KeySignature(4)  # E major
        # Add more transpositions as needed
        return original_key  # Default: return original if not handled


class AudioTranscriber:
    """Handles audio-to-MIDI transcription using generic frequency analysis."""
    
    def __init__(self):
        """Initialize the audio transcriber."""
        self.sr = 22050
        self.hop_length = 512
        self.frame_length = 2048
        self.min_note_duration = 0.1  # Minimum note duration in seconds
        self.onset_threshold = 0.1    # Threshold for onset detection
    
    def _frequency_to_note(self, freq):
        """Convert frequency to music21 note object with proper octave handling."""
        if freq <= 20 or freq > 4000:  # Reasonable frequency range for musical notes
            return None
        
        try:
            # Convert frequency to MIDI note number
            midi_note = librosa.hz_to_midi(freq)
            
            # Round to nearest semitone
            midi_note_rounded = int(round(midi_note))
            
            # Ensure MIDI note is in valid range
            if midi_note_rounded < 21 or midi_note_rounded > 108:  # Piano range
                return None
            
            # Create music21 pitch object
            p = pitch.Pitch(midi=midi_note_rounded)
            return note.Note(p)
        except Exception:
            return None
    
    def _detect_onsets(self, audio, sr):
        """Detect note onsets in audio using spectral flux."""
        # Use librosa's onset detection
        onset_frames = librosa.onset.onset_detect(
            y=audio, 
            sr=sr, 
            hop_length=self.hop_length,
            units='time',
            backtrack=True
        )
        return onset_frames
    
    def _extract_notes_from_audio(self, audio, sr):
        """Extract notes using generic onset detection and frequency analysis."""
        # Detect onsets
        onset_times = self._detect_onsets(audio, sr)
        
        print(f"Debug: Detected {len(onset_times)} onsets at times: {onset_times}")
        
        treble_notes = []
        bass_notes = []
        
        # Analyze each onset
        for onset_time in onset_times:
            # Create analysis window around onset
            window_duration = 0.3  # 300ms window
            start_time = max(0, onset_time - 0.05)  # Start slightly before onset
            end_time = min(len(audio) / sr, start_time + window_duration)
            
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            
            if end_sample > start_sample:
                window = audio[start_sample:end_sample]
                
                # Spectral analysis
                fft = np.fft.fft(window)
                freqs = np.fft.fftfreq(len(window), 1/sr)
                magnitudes = np.abs(fft)
                
                # Only positive frequencies
                pos_freqs = freqs[:len(freqs)//2]
                pos_mags = magnitudes[:len(magnitudes)//2]
                
                # Find spectral peaks
                peak_indices = librosa.util.peak_pick(
                    pos_mags, 
                    pre_max=10, 
                    post_max=10, 
                    pre_avg=5, 
                    post_avg=5, 
                    delta=0.1, 
                    wait=5
                )
                
                # Sort peaks by magnitude
                if len(peak_indices) > 0:
                    peak_freqs = pos_freqs[peak_indices]
                    peak_mags = pos_mags[peak_indices]
                    
                    # Sort by magnitude (descending)
                    sorted_indices = np.argsort(peak_mags)[::-1]
                    
                    # Process the strongest peaks
                    for idx in sorted_indices[:4]:  # Top 4 peaks max
                        freq = peak_freqs[idx]
                        magnitude = peak_mags[idx]
                        
                        # Convert to note
                        note_obj = self._frequency_to_note(freq)
                        if note_obj and magnitude > 0.05:  # Minimum magnitude threshold
                            # Classify as treble or bass based on pitch
                            if note_obj.pitch.ps >= Ranges.MIDDLE_C:
                                treble_notes.append((onset_time, note_obj))
                                print(f"Debug: Treble note at {onset_time:.2f}s: {note_obj.pitch.name}{note_obj.pitch.octave} ({freq:.1f}Hz)")
                            else:
                                bass_notes.append((onset_time, note_obj))
                                print(f"Debug: Bass note at {onset_time:.2f}s: {note_obj.pitch.name}{note_obj.pitch.octave} ({freq:.1f}Hz)")
        
        return treble_notes, bass_notes
    
    
    
    def _create_dynamic_part(self, notes, instrument_obj, clef_obj=None, key_sig=None, audio_duration=None):
        """Create a part with notes distributed dynamically across measures."""
        part = stream.Part()
        part.insert(0, instrument_obj)
        
        if clef_obj:
            part.insert(0, clef_obj)
        if key_sig:
            part.insert(0, key_sig)
        
        if not notes:
            # Create a single empty measure if no notes
            measure = stream.Measure(number=1)
            measure.insert(0, meter.TimeSignature('4/4'))
            if key_sig:
                measure.insert(0, key_sig)
            if clef_obj:
                measure.insert(0, clef_obj)
            measure.insert(0, note.Rest(quarterLength=4.0))
            part.append(measure)
            return part
        
        # Determine audio duration if not provided
        if audio_duration is None:
            audio_duration = max(onset_time for onset_time, _ in notes) + 1.0
        
        # Calculate number of measures needed (assuming 4/4 time, 4 beats per measure)
        beats_per_measure = 4.0
        estimated_tempo = 120  # BPM
        seconds_per_beat = 60.0 / estimated_tempo
        seconds_per_measure = beats_per_measure * seconds_per_beat
        
        num_measures = max(1, int(np.ceil(audio_duration / seconds_per_measure)))
        
        print(f"Debug: Creating {num_measures} measures for {len(notes)} notes over {audio_duration:.2f}s")
        
        # Create measures
        measures = []
        for i in range(num_measures):
            measure = stream.Measure(number=i + 1)
            if i == 0:
                measure.insert(0, meter.TimeSignature('4/4'))
                if key_sig:
                    measure.insert(0, key_sig)
                if clef_obj:
                    measure.insert(0, clef_obj)
            measures.append(measure)
        
        # Distribute notes across measures
        for onset_time, music_note in notes:
            # Calculate which measure and beat offset
            measure_index = min(int(onset_time / seconds_per_measure), num_measures - 1)
            time_in_measure = onset_time % seconds_per_measure
            beat_offset = time_in_measure / seconds_per_beat
            
            print(f"Debug: Note at {onset_time:.2f}s -> measure {measure_index + 1}, beat {beat_offset:.2f}")
            
            # Add note to measure
            measures[measure_index].insert(beat_offset, music_note)
        
        # Add measures to part
        for measure in measures:
            part.append(measure)
        
        return part
    
    
    def _detect_key_signature(self, notes):
        """Detect the most likely key signature from the notes."""
        if not notes:
            return key.KeySignature(0)  # Default to C major
        
        # Collect all pitch classes
        pitch_classes = []
        for _, note_obj in notes:
            pitch_classes.append(note_obj.pitch.pitchClass)
        
        # Count occurrences
        pc_counts = {}
        for pc in pitch_classes:
            pc_counts[pc] = pc_counts.get(pc, 0) + 1
        
        # Simple heuristic: find the most common major/minor key
        # This is a simplified approach - could be enhanced with proper key detection algorithms
        major_keys = {
            0: 0,   # C major (no accidentals)
            7: 1,   # G major (1 sharp)
            2: 2,   # D major (2 sharps) 
            9: 3,   # A major (3 sharps)
            4: 4,   # E major (4 sharps)
            11: 5,  # B major (5 sharps)
            6: 6,   # F# major (6 sharps)
            1: 7,   # C# major (7 sharps)
            5: -1,  # F major (1 flat)
            10: -2, # Bb major (2 flats)
            3: -3,  # Eb major (3 flats)
            8: -4,  # Ab major (4 flats)
        }
        
        # Find most frequent pitch class as potential tonic
        if pc_counts:
            most_common_pc = max(pc_counts, key=pc_counts.get)
            if most_common_pc in major_keys:
                return key.KeySignature(major_keys[most_common_pc])
        
        return key.KeySignature(0)  # Default to C major
    
    def _estimate_note_durations(self, notes):
        """Estimate note durations based on onset timing."""
        if len(notes) <= 1:
            return notes
        
        notes_with_duration = []
        sorted_notes = sorted(notes, key=lambda x: x[0])  # Sort by onset time
        
        for i, (onset_time, note_obj) in enumerate(sorted_notes):
            if i < len(sorted_notes) - 1:
                # Duration until next note
                next_onset = sorted_notes[i + 1][0]
                duration = next_onset - onset_time
            else:
                # Last note gets a default duration
                duration = 0.5
            
            # Quantize duration to common note values
            if duration <= 0.375:  # Eighth note or shorter
                note_obj.quarterLength = 0.5
            elif duration <= 0.75:  # Quarter note
                note_obj.quarterLength = 1.0
            elif duration <= 1.5:   # Half note
                note_obj.quarterLength = 2.0
            else:                   # Whole note or longer
                note_obj.quarterLength = 4.0
            
            notes_with_duration.append((onset_time, note_obj))
        
        return notes_with_duration
    
    
    def transcribe_to_midi(self, audio_path):
        """Transcribe audio file using generic onset detection and frequency analysis."""
        # Load audio
        audio, sr = librosa.load(audio_path, sr=self.sr, mono=True)
        audio_duration = len(audio) / sr
        
        # Extract notes using generic method
        treble_notes, bass_notes = self._extract_notes_from_audio(audio, sr)
        
        print(f"Debug: Extracted {len(treble_notes)} treble notes, {len(bass_notes)} bass notes")
        
        # Estimate note durations
        treble_notes = self._estimate_note_durations(treble_notes)
        bass_notes = self._estimate_note_durations(bass_notes)
        
        # Detect key signature from all notes
        all_notes = treble_notes + bass_notes
        detected_key = self._detect_key_signature(all_notes)
        
        print(f"Debug: Detected key signature: {detected_key}")
        
        # Create music21 score
        score = stream.Score()
        
        # Create treble clef part (right hand)
        treble_part = self._create_dynamic_part(
            treble_notes, 
            instrument.Piano(), 
            clef_obj=clef.TrebleClef(),
            key_sig=detected_key,
            audio_duration=audio_duration
        )
        
        # Create bass clef part (left hand) 
        bass_part = self._create_dynamic_part(
            bass_notes,
            instrument.Piano(),
            clef_obj=clef.BassClef(), 
            key_sig=detected_key,
            audio_duration=audio_duration
        )
        
        # Add both parts to score
        score.insert(0, treble_part)
        score.insert(0, bass_part)
        
        return score


class BrassArranger:
    """Arranges piano scores for brass instruments."""
    
    def __init__(self, input_file):
        """Initialize the brass arranger with a MusicXML or audio file."""
        self.input_file = input_file
        self.is_audio_file = self._is_audio_file(input_file)
        
        if self.is_audio_file:
            # Transcribe audio to score first
            transcriber = AudioTranscriber()
            self.score = transcriber.transcribe_to_midi(input_file)
        else:
            # Parse MusicXML directly
            self.score = converter.parse(input_file)
        
        self.treble_part = None
        self.bass_part = None
        self._extract_parts()
    
    def _is_audio_file(self, file_path):
        """Check if the input file is an audio file."""
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'}
        return os.path.splitext(file_path.lower())[1] in audio_extensions
    
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
    
    def _suppress_key_signature_accidentals(self, note_obj, key_sig):
        """Remove visual accidentals that are already implied by the key signature."""
        if not (hasattr(note_obj.pitch, 'accidental') and note_obj.pitch.accidental):
            return
        
        step = note_obj.pitch.step
        accidental_name = note_obj.pitch.accidental.name
        
        # Get the accidentals implied by the key signature
        key_accidentals = key_sig.alteredPitches
        
        # Check if this note's accidental is implied by the key signature
        for altered_pitch in key_accidentals:
            if (step == altered_pitch.step and 
                accidental_name == altered_pitch.accidental.name):
                note_obj.pitch.accidental.displayStatus = False
                break
    
    def _process_measure_elements(self, source_measure, target_measure, 
                                  transposition_interval=None, 
                                  min_range=None, max_range=None,
                                  key_sig=None):
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
                if key_sig:
                    self._suppress_key_signature_accidentals(new_note, key_sig)
                
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
        # Get original key signature from treble part
        original_key = None
        for element in self.treble_part.getElementsByClass(key.KeySignature):
            original_key = element
            break
        
        if original_key is None:
            original_key = key.KeySignature(0)  # Default to C major
        
        # Transpose key signature for Bb trumpet
        transposed_key = KeySignatures.transpose_key_signature(original_key, Transposition.BB_TRUMPET)
        
        # Set up trumpet part
        trumpet_part = self._setup_instrument_part(
            instrument.Trumpet(), 
            key_sig=transposed_key
        )
        
        # Copy time signatures
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
                key_sig=transposed_key
            )
            
            trumpet_part.append(new_measure)
        
        return trumpet_part
    
    def arrange_for_trombone(self):
        """Arrange the bass part for trombone (concert pitch)."""
        # Get original key signature from bass part
        original_key = None
        for element in self.bass_part.getElementsByClass(key.KeySignature):
            original_key = element
            break
        
        if original_key is None:
            original_key = key.KeySignature(0)  # Default to C major
        
        # Trombone stays in concert pitch, so use original key
        trombone_part = self._setup_instrument_part(
            instrument.Trombone(),
            clef_obj=clef.BassClef(),
            key_sig=original_key
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
                key_sig=original_key
            )
            
            trombone_part.append(new_measure)
        
        return trombone_part
    
    def _get_original_title(self):
        """Extract the original title from the input filename."""
        # Use the filename without extension as the title
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        return base_name
    
    def _create_score_with_metadata(self, title_suffix):
        """Create a new score with properly configured metadata."""
        score = stream.Score()
        original_title = self._get_original_title()
        full_title = f"{original_title} - {title_suffix}"
        
        # Create clean metadata without default Music21 composer
        from music21 import metadata
        score.metadata = metadata.Metadata()
        score.metadata.title = full_title
        score.metadata.movementName = full_title
        # Set composer to empty string to avoid default "Music21"
        score.metadata.composer = ""
        
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
    
    def generate_outputs(self, output_dir="./generated"):
        """Generate all output files (individual parts and duet score)."""
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
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
    # Check for both XML and MP3 files, prioritize MP3 to test audio transcription
    input_files = ["Example.mp3", "Example.xml"]
    input_file = None
    
    for file in input_files:
        if os.path.exists(file):
            input_file = file
            break
    
    if input_file is None:
        print("Error: No input file found. Looking for Example.xml or Example.mp3")
        return
    
    file_type = "audio" if input_file.endswith('.mp3') else "MusicXML"
    print(f"Processing {file_type} file: {input_file}")
    
    arranger = BrassArranger(input_file)
    trumpet_file, trombone_file, duet_file = arranger.generate_outputs()
    
    print("Brass arrangement complete!")
    print("Generated files:")
    print(f"  - Trumpet: {trumpet_file}")
    print(f"  - Trombone: {trombone_file}")
    print(f"  - Brass Duet: {duet_file}")


if __name__ == "__main__":
    main()