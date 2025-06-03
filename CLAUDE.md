# Claude AI Development Guide

This project is designed to work seamlessly with Claude AI for development, debugging, and enhancement. This guide provides Claude-specific configurations and workflows.

## Claude Project Configuration

### Recommended Claude Settings

When working on this project with Claude, use these settings for optimal results:

```
Project Name: Transcriber
Project Type: Python Development
Focus Areas: Music Processing, MusicXML, Algorithm Development
```

### Key Project Context

Claude should be aware of:
- **Primary Technology**: Python 3.8+ with music21 library
- **Package Management**: uv (recommended) or pip for dependency management
- **Project Structure**: Modern Python with pyproject.toml configuration
- **Input Format**: MusicXML piano scores
- **Output Format**: Transposed MusicXML brass arrangements
- **Core Logic**: Instrument transposition, range adjustment, key signature handling
- **Code Style**: Clean, well-documented, object-oriented Python

## Development Workflows

### 1. Feature Development

When adding new instruments or capabilities:

```
1. Analyze the musical requirements (range, transposition, clef)
2. Add constants to the appropriate classes (Ranges, Transposition, etc.)
3. Create or modify arrangement methods
4. Update the main BrassArranger class
5. Add comprehensive tests
6. Update documentation
```

### 2. Bug Fixing

For debugging musical output issues:

```
1. Examine the generated MusicXML files
2. Check pitch ranges and transpositions
3. Verify key signature logic
4. Test with the example file
5. Validate against music theory rules
```

### 3. Code Refactoring

When improving code structure:

```
1. Maintain the existing class hierarchy
2. Preserve all musical logic
3. Keep constants organized and well-documented
4. Ensure backward compatibility
5. Update tests and documentation
```

## Common Claude Tasks

### Adding New Instruments

**Prompt Template:**
```
I want to add support for [INSTRUMENT] to the AI music transcription tool. 
This instrument:
- Transposes: [TRANSPOSITION] 
- Range: [LOW_NOTE] to [HIGH_NOTE]
- Clef: [CLEF]
- Key signature needs: [KEY_SIG_LOGIC]

Please help me implement this following the existing patterns in the codebase.
```

### Debugging Musical Issues

**Prompt Template:**
```
The generated [INSTRUMENT] part has an issue with [SPECIFIC_PROBLEM]. 
Here's the relevant MusicXML output: [XML_SNIPPET]
The expected behavior should be: [EXPECTED_RESULT]
Please help me debug and fix this issue.
```

### Code Quality Improvements

**Prompt Template:**
```
Please review the [FILE/METHOD] for potential improvements in:
- Code readability and maintainability
- Performance optimization
- Music theory accuracy
- Python best practices
Following the existing code style and patterns.
```

## File Structure for Claude Context

When working with Claude, provide context about:

### Core Files
- `src/transcriber/brass_arranger.py` - Main arrangement logic
- `src/transcriber/__init__.py` - Package initialization
- `examples/Example.xml` - Test input file

### Configuration Files
- `pyproject.toml` - Package configuration and dependencies (uv/modern)
- `requirements.txt` - Python dependencies (legacy compatibility)
- `.python-version` - Python version specification for uv
- `README.md` - User documentation

### Development Files
- `TODO.md` - Feature roadmap
- `tests/` - Unit tests (when created)
- `docs/` - Additional documentation

## Testing with Claude

### Verification Checklist

When Claude makes changes, verify:

- [ ] **Musical Accuracy**: Correct transpositions and key signatures
- [ ] **Code Quality**: Follows existing patterns and style
- [ ] **Compatibility**: Works with existing example files
- [ ] **Documentation**: Updates README and comments as needed
- [ ] **No Regressions**: Existing functionality still works

### Test Commands

#### With uv (Recommended)

```bash
# Test basic functionality
cd examples
uv run python -m transcriber.brass_arranger

# Or activate the environment first
uv shell
python -m transcriber.brass_arranger

# Check output files
ls -la Example_*.xml

# Verify MusicXML structure
head -n 50 Example_Trumpet.xml

# Run tests
uv run pytest tests/
```

#### With pip (Traditional)

```bash
# Test basic functionality
cd examples
python -m transcriber.brass_arranger

# Check output files
ls -la Example_*.xml

# Verify MusicXML structure
head -n 50 Example_Trumpet.xml
```

## Music Theory Context for Claude

### Key Concepts
- **Bb Instruments**: Written pitch is major 2nd higher than concert pitch
- **Key Signatures**: Transpose with the instrument (C major → D major for Bb trumpet)
- **Accidentals**: Suppress sharps/flats already in key signature
- **Ranges**: Keep notes within comfortable playing ranges for each instrument

### Common Transpositions
- **Bb Trumpet**: Up major 2nd (C → D)
- **F Horn**: Up perfect 5th (C → G)
- **Eb Alto Sax**: Up major 6th (C → A)
- **Concert Pitch**: Trombone, flute, oboe, violin

## Collaboration Best Practices

### When Requesting Changes
1. **Be Specific**: Describe exact musical or technical requirements
2. **Provide Examples**: Include MusicXML snippets or expected outputs
3. **Consider Impact**: Mention if changes affect other instruments/features
4. **Test Thoroughly**: Verify changes work with provided example files

### When Reviewing Claude's Work
1. **Test Musical Output**: Listen to or examine generated files
2. **Check Code Style**: Ensure consistency with existing patterns
3. **Verify Documentation**: Confirm README and comments are updated
4. **Consider Edge Cases**: Test with different input scenarios

## Useful Claude Prompts

### Quick Tasks
- "Fix the [INSTRUMENT] range to be [RANGE]"
- "Add support for [TIME_SIGNATURE] time signatures"
- "Improve error handling for invalid MusicXML files"
- "Optimize the note processing loop for better performance"

### Complex Features
- "Implement a new instrument arrangement system for [INSTRUMENT_FAMILY]"
- "Add harmonic analysis to improve voice leading"
- "Create a plugin system for custom arrangement algorithms"
- "Build a configuration system for user-defined instrument settings"

---

This configuration helps Claude understand the project's musical and technical context, enabling more effective collaboration on music transcription and arrangement features.