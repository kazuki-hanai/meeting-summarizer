from openai import OpenAI
from typing import Any
import asyncio
import aiohttp
import os
import sys
import subprocess
from pathlib import Path

def spliit_audio(input_file: str, output_dir: str = "output", segment_duration: int = 50) -> None | Exception:
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        return Exception(f"Error creating output directory: {e}")

    base_name = Path(input_file).stem

    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-f", "segment",
        "-segment_time", str(segment_duration),
        "-c:a", "pcm_s16le",
        "-ar", "44100",
        os.path.join(output_dir, f"{base_name}_%03d.wav")
    ]

    try:
        _ = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        return Exception(f"Error executing ffmpeg: {e}")

async def transcribe_audio(client: OpenAI, audio_file_path: str) -> dict[str, str]:
    async with aiohttp.ClientSession() as session:
        with open(audio_file_path, "rb") as audio_file:
            form = aiohttp.FormData()
            form.add_field('file', audio_file, filename=os.path.basename(audio_file_path))
            form.add_field('model', 'whisper-1')
            
            async with session.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {client.api_key}"},
                data=form
            ) as response:
                result: object = await response.json()
                return {
                    "file": audio_file_path,
                    "transcription": result.get("text", "")
                }


async def main():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    args = sys.argv

    def help() -> str:
        return "python main.py <audio_file> <audio_output_dir> <transcibe_result_file>\ne.g. python main.py audio.m4a output result.txt"

    if len(args) < 3:
        print(help())
        return

    audio_file = args[1]
    if not os.path.exists(audio_file):
        print("Output file does not exist")
        print(help())
        exit(1)

    audio_output_dir = args[2]
    if audio_output_dir == "":
        print("Please provide an output directory")
        print(help())
        return

    transcribe_result_file = args[3]
    if transcribe_result_file == "":
        print("Please provide a result file")
        print(help())
        return

    # Split audio file
    e = spliit_audio(audio_file, audio_output_dir)
    if e:
        raise e
    print("File split and converted to WAV successfully!")

    # List audio files from audio_dir and sort
    audio_files = os.listdir(audio_output_dir)
    audio_files.sort()

    tasks: list[asyncio.Task[Any]] = []

    for audio_file in audio_files:
        if not audio_file.endswith(".wav"):
            continue

        audio_file_path = os.path.join(audio_output_dir, audio_file)
        task: asyncio.Task[Any] = asyncio.create_task(transcribe_audio(client, audio_file_path))
        tasks.append(task)

    results: list[dict[str, str]] = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"File: {result['file']}")
        print(f"Transcription: {result['transcription']}")
        print("---")

    results.sort(key=lambda x: x["file"])

    summary_prompt = "Summarize the transcriptions of the audio files. Please contain the details of conversations."
    summary_prompt += "\n\n"
    summary_prompt += "```\n"
    for result in results:
        summary_prompt += f"{result['transcription']}\n"
    summary_prompt += "```"

    summary = client.chat.completions.create(
        model = "gpt-4o",
        messages = [{"role": "system", "content": summary_prompt}]
    )   

    with open(transcribe_result_file, "w") as output_file:
        for result in results:
            _ = output_file.write(f"{result['transcription']}\n")
        _ = output_file.write("\n\n")
        _ = output_file.write("Summary:\n")
        _ = output_file.write(summary.choices[0].message.content or "")

if __name__ == "__main__":
    asyncio.run(main())
