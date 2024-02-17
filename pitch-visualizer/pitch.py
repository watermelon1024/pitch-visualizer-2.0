import os
import subprocess
import tempfile
import warnings
from functools import partial

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import parselmouth

from .progress import ProgressBar
from .tone import Tonality


class PitchConverter:
    progress_bar: ProgressBar
    resolution: tuple[int, int] = None

    def __init__(
        self,
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
        self.audio_path = audio
        self.video_path = video
        self.output_path = output
        self.tone = tone
        self.fps = fps
        self.dt = 1 / fps
        self.gpu = gpu
        self.ffmpeg = ffmpeg
        self.pitch_width = pitch_width
        self.pitch_position = pitch_position
        self.min_freq = min_freq
        self.max_freq = max_freq

    def __call__(self, *args, **kwds):
        return self.run()

    def run(self):
        self.get_video_resolution()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = self.generate_pitch_video(tmpdir)
            self.combine_video(output_paths)

    def get_video_resolution(self) -> tuple[int, int]:
        if self.resolution:
            return self.resolution

        if self.pitch_width:
            self.resolution = (self.pitch_width, self.pitch_width / 16 * 9)
            return self.resolution

        process = subprocess.run(
            [
                # fmt: off
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=s=x:p=0",
                self.video_path,
                # fmt: on
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.resolution = tuple(map(int, process.stdout.decode().split("x")))
        return self.resolution

    def generate_pitch_video(self, output_dir) -> list[str]:
        # Get all the pitch in the audio and plot it
        sound = parselmouth.Sound(self.audio_path)
        pitch = sound.to_pitch_ac(pitch_floor=self.min_freq, pitch_ceiling=self.max_freq)
        # Get vocal and draw
        # vocal
        pitch_values = pitch.selected_array["frequency"]
        pitch_values[pitch_values == 0] = np.nan
        # time
        pitch_xs = pitch.xs()
        total_frames_count = int(sound.xmax * self.fps)

        plt.rcParams.update({"font.size": 9})
        # create figure
        fig = plt.figure(figsize=(9.6, 5.4), layout="tight", dpi=100)
        # resolution: tuple(r / 200 for r in self.resolution)
        ax = fig.add_subplot(1, 1, 1)
        # Y-axis
        ax.get_yaxis().set_visible(False)
        ax.set_yscale("log")
        ax.set_ylabel("fundamental frequency [Hz]")
        pitch_low = 256 * 0.7
        pitch_high = 256 * 1.7
        ax.set_ylim(pitch_low, pitch_high)
        # tone standard line
        tone_labels: list[plt.Text] = []
        for tone, f in Tonality(self.tone).get_tone_and_freq(self.min_freq, self.max_freq):
            ax.axhline(y=f, color="blue")
            y = f + 0.02
            text = ax.text(1.02, y, tone, ha="left", va="bottom", fontsize=10)
            text.set_visible(pitch_low <= y <= pitch_high)
            tone_labels.append(text)
        # X-axis
        # ax.set_xlim(sound.xmin, sound.xmax)
        # draw mid line (current time)
        mid_line = ax.axvline(0, color="red")
        # draw vocal date
        ax.plot(pitch_xs, pitch_values, ".", markersize=5, color="orange")

        print("Generating pitch video")
        output_paths: list[str] = []
        with ProgressBar(total=total_frames_count) as progress_bar:
            self.progress_bar = progress_bar
            output_path = self.generate_animate(
                fig,
                ax,
                range(total_frames_count),
                pitch_xs,
                pitch_values,
                tuple(tone_labels),
                mid_line,
                os.path.join(output_dir, "pitch.mp4"),
            )
            output_paths.append(output_path)

        plt.close("all")
        return output_paths

    def generate_animate(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        range_obj: range,
        time: np.ndarray,
        pitch: np.ndarray,
        tone_labels: tuple[plt.Text],
        mid_line: plt.Line2D,
        output_path: str,
    ):
        # print(f"Gen output_path: {output_path}, time: {range_obj[0]}-{range_obj[-1]}")
        ani = animation.FuncAnimation(
            fig,
            partial(
                self.animate,
                ax=ax,
                time=time,
                pitch=pitch,
                mid_line=mid_line,
                tone_labels=tone_labels,
            ),
            frames=range_obj,
        )
        ani.save(output_path, writer=animation.FFMpegWriter(fps=self.fps))
        # print(f"Done output_path: {output_path}")
        return output_path

    def animate(
        self,
        frame_idx: int,
        ax: plt.Axes,
        time: np.ndarray,
        pitch: np.ndarray,
        mid_line: plt.Line2D,
        tone_labels: list[plt.Text],
    ):
        curr_time = frame_idx / self.fps
        time_start = curr_time - 2.5
        time_end = curr_time + 2.5
        mid_line.set_data([[curr_time, curr_time], [0, 1]])

        if time_start % 1 == 0:
            time_start -= self.dt
            time_end += self.dt

        # Calculate the average pitch only with the middle part of pitch_vals
        # np.nanmean will generate a warning if all values are nan, ignore it
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            pitch_in_range = pitch[(time >= curr_time - 0.4) & (time <= curr_time + 0.4)]
            avr_pitch = np.nanmean(pitch_in_range)

        if not np.isnan(avr_pitch):
            pitch_low = avr_pitch * 0.7  # 0.7071067811865476
            pitch_high = avr_pitch * 1.7  # 1.8171205928321397
            ax.set_ylim(pitch_low, pitch_high)

            # Set labels' visibilities based on pitch
            for label in tone_labels:
                _, y = label.get_position()
                label.set_visible(pitch_low <= y <= pitch_high)

        for label in tone_labels:
            _, y = label.get_position()
            label.set_position((time_start + 0.02, y))

        ax.set_xlim(time_start, time_end)
        # print(time_start, time_end)

        self.progress_bar.advance()

    def combine_video(self, pitch_paths: list[str]):
        print("Combining video")
        print(f"Writing to {os.path.abspath(self.output_path)}")

        inputs = []
        for path in [self.video_path, *pitch_paths]:
            if self.gpu:
                # 使用 NVIDIA CUDA 加速
                inputs.extend(("-hwaccel", "cuvid", "-hwaccel_output_format", "cuda"))
            inputs.extend(("-i", path))

        subprocess.run(
            [
                # fmt: off
                self.ffmpeg,
                "-loglevel", "error",
                "-stats",
                *inputs,
                "-c:v", "h264_nvenc",  # 使用 NVIDIA NVENC 編碼器
                "-filter_complex",
                f"[0:v]hwupload [base];"
                # Scale the pitch video to half of the original video
                f"[1:v]hwupload,scale_cuda={self.pitch_width or self.resolution[0] // 2}:-1 [pitch];"
                # combine the video
                f"[base][pitch]overlay_cuda={self.pitch_position} [outv]",
                "-map", "[outv]",
                "-map", "0:a",
                self.output_path,
                # fmt: on
            ],
            check=True,
        )
