
import argparse
import asyncio
import sys
import os
from rich.console import Console
from rich.table import Table
from edge_tts import list_voices
from .core import create_audio_from_srt

class CustomHelpFormatter(argparse.HelpFormatter):
    """Custom help formatter to append a filtered list of voices."""
    def format_help(self):
        help_text = super().format_help()
        try:
            voices = asyncio.run(list_voices())
            filtered_voices = [
                v for v in voices 
                if v['Locale'].startswith('en-') or v['Locale'].startswith('zh-')
            ]
            table = Table(
                title="Available Chinese and English Voices",
                show_header=True, 
                header_style="bold cyan"
            )
            table.add_column("Voice ID (for --voice)", style="bold green", width=35)
            table.add_column("Gender", width=8)
            table.add_column("Locale", width=10)
            table.add_column("Description")
            for voice in sorted(filtered_voices, key=lambda v: v['Locale']):
                table.add_row(voice['Name'], voice['Gender'], voice['Locale'], voice['FriendlyName'])
            console = Console()
            with console.capture() as capture:
                console.print(table)
            help_text += "\n\n" + capture.get()
        except Exception as e:
            help_text += f"\n\nCould not fetch voices list: {e}"
        return help_text

def main():
    parser = argparse.ArgumentParser(
        description='Generate synced audio or video from an SRT file using edge-tts.',
        formatter_class=CustomHelpFormatter
    )
    parser.add_argument('srt_file', help='The path to the SRT file.')
    parser.add_argument(
        '--video',
        help='Optional path to a source video file. If provided, output will be a video file.'
    )
    parser.add_argument(
        '--voice',
        default='en-US-AvaMultilingualNeural',
        help='The voice for speech synthesis. Default: en-US-AvaMultilingualNeural.'
    )
    parser.add_argument(
        '--output',
        help='Path for the output file. Defaults to output.mp4 if --video is used, otherwise output.mp3.'
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=10,
        help='Number of concurrent TTS requests. Default: 10'
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Determine default output file name if not provided
    if not args.output:
        if args.video:
            args.output = 'output.mp4'
        else:
            args.output = 'output.mp3'

    try:
        asyncio.run(create_audio_from_srt(
            srt_file=args.srt_file, 
            voice=args.voice, 
            output_file=args.output, 
            concurrency=args.concurrency, 
            video_path=args.video
        ))
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
