from rich.progress import (
    Progress,
    Task,
    TaskID,
    TimeRemainingColumn,
    TimeElapsedColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
    TransferSpeedColumn,
)
from rich.text import Text


class CustomTimeElapsedColumn(TimeElapsedColumn):
    """Renders time elapsed."""

    def render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("--:--", style="progress.elapsed")
        minutes, seconds = divmod(max(0, int(elapsed)), 60)
        return Text(f"{minutes:02d}:{seconds:02d}", style="progress.elapsed")


class CustomTransferSpeedColumn(TransferSpeedColumn):
    """Renders transfer speed."""

    def render(self, task: "Task") -> Text:
        """Show data transfer speed."""
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("?", style="progress.data.speed")
        return Text(f"{speed:.2f}frame/s", style="progress.data.speed")


class ProgressBar:
    progress: Progress
    task: TaskID

    def __init__(self, total: int):
        self.total = total
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            TaskProgressColumn(),
            BarColumn(),
            MofNCompleteColumn(),
            CustomTimeElapsedColumn(),
            TextColumn("<"),
            TimeRemainingColumn(compact=True),
            CustomTransferSpeedColumn(),
            refresh_per_second=5,
        )
        self.progress.start()
        self.task = self.progress.add_task("[cyan]Generating...", total=self.total)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.progress.stop()

    def advance(self, step: int = 1):
        self.progress.update(self.task, advance=step)
