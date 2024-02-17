import re
import shutil

import click

from . import tone
from .pitch import PitchConverter


@click.command(
    "pitch-converter",
    help="""
    AUDIO: The path to the song pitch audio\n
    VIDEO: The path to the song video
    """,
)
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
@click.option("--gpu", is_flag=True, help="Enable GPU acceleration (require NVIDIA CUDA)")
@click.option(
    "--ffmpeg",
    type=click.Path(exists=True, executable=True),
    default=None,
    help="Path to the ffmpeg executable",
)
@click.option("--pitch_width", type=int, default=None)
@click.option(
    "--pitch-position",
    type=str,
    default="top_right",
    help="""
    The position to the stick pitch graph,
    can be [top_right|top_left|bottom_right|bottom_left]
    or specify custom coordinates (x:y)
    """
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
        if ffmpeg is None:
            print("Unable to locate ffmpeg, use --ffmpeg to specify the path to ffmpeg")
            exit(1)

    pitch_position_ = {
        "top_right": "W-w-10:10",
        "top_left": "10:10",
        "bottom_right": "W-w-10:H-h-10",
        "bottom_left": "10:H-h-10",
    }.get(pitch_position)
    if pitch_position_ is None:
        if re.match(r"^\d+:\d+$", pitch_position):
            x, y = pitch_position.split(":")
            pitch_position_ = f"{x}:{y}"
        else:
            print("Invalid pitch position")
            exit(1)

    PitchConverter(
        audio=audio,
        video=video,
        output=output or ".".join(video.split(".")[:-1]) + "_with_pitch.mp4",
        tone=tone_,
        fps=fps,
        gpu=gpu,
        ffmpeg=ffmpeg,
        pitch_width=pitch_width,
        pitch_position=pitch_position_,
        min_freq=tone.Tonality.normalize_to_freq(min_pitch),
        max_freq=tone.Tonality.normalize_to_freq(max_pitch),
    )()


if __name__ == "__main__":
    _main_()
