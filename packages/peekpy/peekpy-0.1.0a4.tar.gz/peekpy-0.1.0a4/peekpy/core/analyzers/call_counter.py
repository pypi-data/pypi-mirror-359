"""CallCounter Analyzer for PeekPy.
Counts the number of times a function is called and stores the count in the stats manager.
"""

from peekpy.core.utils import get_full_name, get_path_file_location
from peekpy.storage import stats_manager
from peekpy.core.analyzers.base_analyzer import BaseAnalyzer


class CallCounter(BaseAnalyzer):
    """
    Analyzer that counts the number of times a function is called.
    Inherits from BaseAnalyzer and implements the analyze method.
    """

    def after(self, func, *args, **kwargs):
        """Method to be called after the function execution.
        Increments the call count for the function in the stats manager."""
        full_name = get_full_name(func)
        path = get_path_file_location(func)
        stats = stats_manager.get_stats().get(full_name, {})

        if "calls_count" not in stats:
            stats["calls_count"] = 0
        stats["calls_count"] += 1
        stats["path"] = path
        stats_manager.add_stats(full_name, stats)
