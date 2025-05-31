# AI-Assisted Music Transcription Tool

A Python library for converting piano scores to brass instrument arrangements. This tool takes MusicXML piano scores and automatically arranges them for trumpet and trombone with proper transposition, key signatures, and musical notation conventions.

## Features

- 🎺 **Trumpet arrangements** with Bb transposition and D major key signatures
- 🎵 **Trombone arrangements** with bass clef and proper range adjustments  
- 🎼 **Combined brass duet scores** with both instruments
- ✨ **Professional notation** with suppressed redundant accidentals
- 📄 **MusicXML output** compatible with all major music notation software

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-music-transcription.git
cd ai-music-transcription

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Basic Usage

```python
from ai_music_transcription import BrassArranger

# Create arranger instance
arranger = BrassArranger("path/to/piano_score.xml")

# Generate all arrangements
trumpet_file, trombone_file, duet_file = arranger.generate_outputs()

print(f"Generated arrangements:")
print(f"  - Trumpet: {trumpet_file}")
print(f"  - Trombone: {trombone_file}")
print(f"  - Brass Duet: {duet_file}")
```

### Command Line Usage

```bash
# Run the example
cd examples
python -m ai_music_transcription.brass_arranger
```

## Example

The `examples/` directory contains a sample piano score (`Example.xml`) that demonstrates the tool's capabilities. Running the tool generates three output files:

- `Example_Trumpet.xml` - Trumpet part in D major with Bb transposition
- `Example_Trombone.xml` - Trombone part in bass clef at concert pitch
- `Example_BrassDuet.xml` - Combined score with both instruments

## How It Works

1. **Part Extraction**: Automatically separates treble and bass clef parts from piano scores
2. **Instrument Adaptation**: 
   - Transposes trumpet parts up a major 2nd for Bb instruments
   - Sets trombone parts in bass clef at concert pitch
3. **Musical Intelligence**:
   - Adjusts notes to comfortable instrument ranges
   - Applies correct key signatures (D major for trumpet, C major for trombone)
   - Suppresses redundant accidentals already implied by key signatures
4. **Professional Output**: Generates properly formatted MusicXML files

## Supported Input Formats

- **MusicXML** (.xml, .musicxml) - Piano scores with separate treble/bass parts or combined parts

## Output Formats

- **MusicXML** (.xml) - Compatible with:
  - MuseScore
  - Finale
  - Sibelius
  - Dorico
  - And other music notation software

## Requirements

- Python 3.8+
- music21 library
- MusicXML input files

## Development

### Project Structure

```
ai-music-transcription/
├── src/ai_music_transcription/     # Main package code
│   ├── __init__.py
│   └── brass_arranger.py          # Core arrangement logic
├── examples/                      # Example input files
│   └── Example.xml               # Sample piano score
├── tests/                        # Unit tests
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
├── setup.py                    # Package setup
├── README.md                   # This file
├── LICENSE                     # MIT license
└── TODO.md                    # Future enhancements
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=ai_music_transcription tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Claude AI Integration

This project is designed to work seamlessly with Claude AI for code development and enhancement. See `CLAUDE.md` for Claude-specific configuration and workflows.

## Roadmap

See [TODO.md](TODO.md) for planned features and enhancements, including:

- Audio input support (MP3, WAV, etc.)
- Image/PDF sheet music recognition
- Additional instrument arrangements (woodwinds, strings)
- Audio playback generation
- Advanced harmonic analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [music21](https://web.mit.edu/music21/) library
- Developed with assistance from Claude AI
- MusicXML format by MakeMusic/Steinberg

## Support

- 📖 Check the [documentation](docs/)
- 🐛 Report bugs via [GitHub Issues](https://github.com/your-username/ai-music-transcription/issues)
- 💡 Request features via [GitHub Discussions](https://github.com/your-username/ai-music-transcription/discussions)