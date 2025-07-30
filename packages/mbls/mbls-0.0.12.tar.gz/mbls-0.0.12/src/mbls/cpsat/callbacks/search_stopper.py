import threading
from typing import Callable, Optional

# TODO: test and add to __init__.py


class SearchStopper:
    """
    Utility to stop a search process after a given period with no improvement (or any event).
    Can be used with OR-Tools CpSolverSolutionCallback.StopSearch, or any user-defined callback.

    Args:
        stop_callback (Callable[[], None]): Function to call for stopping the search.
        improve_time_limit (float): Time (in seconds) after which to trigger stop_callback if not reset.

    Usage:
        stopper = SearchStopper(solver.StopSearch, 60)
        # 어떤 개선점이 나올 때마다 stopper.reset_timer()
        # 타이머 해제는 stopper.cancel_timer()
    """

    def __init__(
        self, stop_callback: Callable[[], None], improve_time_limit: float = 60.0
    ):
        self.stop_callback = stop_callback
        self.improve_time_limit = improve_time_limit
        self._timer: Optional[threading.Timer] = None
        self.stopped = False
        self._lock = threading.Lock()

    def reset_timer(self, new_time_limit: Optional[float] = None):
        """(Re)start the timer. If new_time_limit is provided, update the limit."""
        with self._lock:
            if new_time_limit is not None:
                self.improve_time_limit = new_time_limit
            self.cancel_timer()
            if self.improve_time_limit > 0:
                self._timer = threading.Timer(self.improve_time_limit, self._on_timeout)
                self._timer.start()
                self.stopped = False

    def cancel_timer(self):
        """Cancel the running timer, if any."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def _on_timeout(self):
        with self._lock:
            if not self.stopped:
                self.stop_callback()
                self.stopped = True
                self._timer = None

    def is_running(self) -> bool:
        """Check if the timer is currently running."""
        return self._timer is not None and self._timer.is_alive()

    def mark_stopped(self):
        """Manually mark as stopped (if stop_callback is called externally)."""
        with self._lock:
            self.stopped = True
            self.cancel_timer()

    def __del__(self):
        self.cancel_timer()
