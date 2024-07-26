# meeting-summarizer

## Pre-requisites
- poetry
- OpenAI API key
- ffmpeg

## Usage

This script does the following:
1. Split input audio file into chunks to avoid API limits
2. Transcribe audio chunks to text using Whisper API and output to a text file

```mermaid
flowchart TD
subgraph Z[" "]
direction LR
    A[Input audio file] -->|ffmpeg| B[Audio chunks...]
    B --> |Whisper API| C[Transcription and Summary]
end
```

To run the script, execute the following command:
```
poetry install
poetry run python main.py <audio_file>
# e.g. poetry run python main.py audio.mp3
```

Then, chunks are outputed to <audio>_chunks and transcriptions are outputed to <audio>_transcriptions.txt
