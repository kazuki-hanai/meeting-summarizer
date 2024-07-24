# audio-to-text

## Pre-requisites
- poetry
- Whisper API key
- ffmpeg

## Usage

This script does the following:
1. Split audio file into chunks to avoid API limits
2. Transcribe audio chunks to text using Whisper API

To run the script, execute the following command:
```
poetry install
poetry run python main.py <input_audio_file> <audio_output_dir> <output_text_file>
```
