"""
Stopwatch timer module for tracking game duration.
"""

import time


class Timer:
    """
    Precision stopwatch tracking elapsed game time in seconds with pause/resume support.
    """
    def __init__(self, initial_elapsed: int = 0):
        self.accumulated_seconds: float = float(initial_elapsed)
        self.start_time: float = 0.0
        self.is_running: bool = False

    def start(self):
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def pause(self):
        if self.is_running:
            self.accumulated_seconds += (time.time() - self.start_time)
            self.is_running = False

    def reset(self):
        self.accumulated_seconds = 0.0
        self.start_time = time.time() if self.is_running else 0.0

    def get_elapsed_seconds(self) -> int:
        if self.is_running:
            return int(self.accumulated_seconds + (time.time() - self.start_time))
        return int(self.accumulated_seconds)

    def get_formatted_time(self) -> str:
        total = self.get_elapsed_seconds()
        mins = total // 60
        secs = total % 60
        return f"{mins:02d}:{secs:02d}"
