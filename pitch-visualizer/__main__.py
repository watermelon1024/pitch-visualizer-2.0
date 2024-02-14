# __main__.py

import os
import shutil
import click

from . import tone
from .main import main


@click.command()
@click.argument("audio", type=click.Path(exists=True), required=True)  # Path to the song audio
@click.argument("video", type=click.Path(exists=True), required=True)  # Path to the song video
@click.option(
    "--output", "-o", type=click.Path(), default=None, help="Path to the output video file"
)
@click.option(
    "--tone",
    "-t",
    "tone_",
    type=click.Choice(tone.TONES),
    required=True,
    help="The tone of the song",
)
@click.option("--fps", type=int, help="The fps of output video", default=15)
@click.option("--gpu", is_flag=True, help="Enable GPU acceleration")
@click.option(
    "--ffmpeg",
    type=click.Path(exists=True, executable=True),
    default=None,
    help="Path to the ffmpeg executable",
)
@click.option("--pitch_width", type=int, default=None)
@click.option(
    "--pitch-position",
    type=click.Choice(
        ["top_right", "top_left", "bottom_right", "bottom_left"], case_sensitive=False
    ),
    default="top_right",
)
@click.option("--min-pitch", type=click.Choice(tone.TONE_FREQ_MAP.keys()), default="D2")
@click.option("--max-pitch", type=click.Choice(tone.TONE_FREQ_MAP.keys()), default="G5")
def _main_(
    audio: str,
    video: str,
    output: str,
    tone_: str,
    fps: int,
    gpu: bool,
    ffmpeg: str,
    pitch_width: int,
    pitch_position: str,
    min_pitch: str,
    max_pitch: str,
):
    if ffmpeg is None:
        ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None or not os.path.exists(ffmpeg):
        print("Unable to locate ffmpeg, use --ffmpeg to specify the path to ffmpeg")
        exit(1)

    main(
        audio=audio,
        video=video,
        output=output or ".".join(video.split(".")[:-1]) + "_with_pitch.mp4",
        tone=tone_,
        fps=fps,
        gpu=gpu,
        ffmpeg=ffmpeg,
        pitch_width=pitch_width,
        pitch_position=pitch_position,
        min_freq=tone.Tonality.normalize_to_freq(min_pitch),
        max_freq=tone.Tonality.normalize_to_freq(max_pitch),
    )


if __name__ == "__main__":
    _main_()
