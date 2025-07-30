# cakesrt2audio

Generate audio from SRT files using Microsoft Edge's text-to-speech service.

This tool synchronizes audio with SRT timestamps, adjusting playback speed within a specified tolerance, and logs any significant deviations.

## Installation

```bash
pip install cakesrt2audio
```

## Usage

### As a Library

```python
from cakesrt2audio import create_audio_from_srt

create_audio_from_srt(
    srt_file="path/to/your.srt",
    voice="en-US-AvaMultilingualNeural", 
    output_file="path/to/output.mp3"
)
```

### From the Command Line

```bash
python -m cakesrt2audio your.srt --voice en-US-AvaMultilingualNeural --output output.mp3
```

To see a list of all available voices:

```bash
python -m cakesrt2audio --help
```
