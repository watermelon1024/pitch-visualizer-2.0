def main(
    audio: str,
    video: str,
    output: str,
    tone: str,
    fps: int,
    gpu: bool,
    ffmpeg: str,
    pitch_width: int,
    pitch_position: str,
    min_freq: str,
    max_freq: str,
):
    print(
        f"""\
{'audio':17}: {audio}
{'video':17}: {video}
{'output':17}: {output}
{'music tone':17}: {tone}
{'fps':17}: {fps}
{'GPU acceleration':17}: {gpu}
{'ffmpeg path':17}: {ffmpeg}
{'pitch width':17}: {pitch_width}
{'pitch position':17}: {pitch_position}
{'min freq':17}: {min_freq}
{'max freq':17}: {max_freq}
        """
    )
    ...
