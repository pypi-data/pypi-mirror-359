import logging

from mbls import ElapsedTimer


class ObjectiveBoundRecorder:
    """
    Callable object to record (elapsed time, objective bound) pairs.

    Args:
        e_timer (ElapsedTimer | None): Timer to measure elapsed time.
            If None, a new ElapsedTimer is created and started.
        print_on_call (bool): If True, prints each record.
        call_log_level (int | None): If set, logs each record at this logging level.

    Attributes:
        elapsed_time_and_bound (list[tuple[float, float]]): List of (elapsed_sec, objective bound) pairs.
    """

    def __init__(
        self,
        e_timer: ElapsedTimer | None = None,
        print_on_call: bool = False,
        call_log_level: int | None = None,
    ) -> None:
        """
        Args:
            e_timer (ElapsedTimer | None, optional): Timer for measuring elapsed time.
                If None, a new ElapsedTimer is created and started.
            print_on_call (bool, optional): If True, prints progress at each call.
                Defaults to False.
            call_log_level (int | None, optional): If set to a valid logging level,
                logs the progress message at that level.
                Defaults to None.
        """
        if e_timer is None:
            e_timer = ElapsedTimer()
            e_timer.set_start_time_as_now()
        self._e_timer = e_timer
        """Elapsed timer to track the time. If None, a new ElapsedTimer is created and started."""

        self.print_on_call = print_on_call
        """If True, prints progress on each call."""

        self.call_log_level = call_log_level
        """If set, logs progress at the specified logging level."""

        self.elapsed_time_and_bound: list[tuple[float, float]] = []
        """A list of tuples containing (elapsed time, objective bound)."""

    def __call__(self, obj_bound: float):
        elapsed_sec = self._e_timer.elapsed_sec
        self.elapsed_time_and_bound.append((elapsed_sec, obj_bound))

        info_str = f"Elapsed: {elapsed_sec:.2f} sec, Obj. bound: {obj_bound}"
        if self.print_on_call:
            print(info_str)
        if (
            self.call_log_level is not None
            and 10 <= self.call_log_level <= 50
            and self.call_log_level in logging._levelToName
        ):
            logging.log(self.call_log_level, info_str)
