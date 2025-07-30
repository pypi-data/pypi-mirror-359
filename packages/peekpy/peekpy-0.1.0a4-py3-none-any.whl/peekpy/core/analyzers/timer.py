"""Timer analyzer for PeekPy."""

import time
from peekpy.core.utils import get_full_name, get_path_file_location
from peekpy.storage import stats_manager
from peekpy.core.analyzers.base_analyzer import BaseAnalyzer


class TimerCount(BaseAnalyzer):
    """Analyzer that measures the execution time of a function.
    Inherits from BaseAnalyzer and implements the before and after
    methods to track the time taken by the function."""

    def __init__(self):
        self.start_time = None

    def before(self, func, *args, **kwargs):
        """Method to be called before the function execution.
        Initializes the start time for measuring execution duration."""
        self.start_time = time.perf_counter()

    def after(self, func, *args, **kwargs):
        """Method to be called after the function execution.
        Calculates the elapsed time and updates the stats manager with the execution time.
        """
        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time

        full_name = get_full_name(func)
        path = get_path_file_location(func)

        stats = stats_manager.get_stats().get(full_name, {})

        if "times" not in stats:
            stats["times"] = []
        stats["path"] = path
        stats["times"].append(elapsed_time)

        stats_manager.add_stats(full_name, stats)
