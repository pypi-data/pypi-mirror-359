import logging

from ortools.sat.python.cp_model import CpSolverSolutionCallback

from mbls import ElapsedTimer


class ObjectiveValueRecorder(CpSolverSolutionCallback):
    """
    Solution callback that records (elapsed time, objective value) pairs
    at each solution found during the CP-SAT search.

    Args:
        e_timer (ElapsedTimer | None): Timer for measuring elapsed time.
            If None, a new ElapsedTimer is created and started.
        print_on_callback (bool): If True, prints progress at each solution callback.
        callback_log_level (int | None): If set, logs progress at the specified logging level.

    Attributes:
        elapsed_time_and_value (list[tuple[float, float]]): List of (elapsed time, objective value) pairs.
    """

    def __init__(
        self,
        e_timer: ElapsedTimer | None = None,
        print_on_callback: bool = False,
        callback_log_level: int | None = None,
    ) -> None:
        """
        Args:
            e_timer (ElapsedTimer | None, optional): Timer for measuring elapsed time.
                If None, a new ElapsedTimer is created and started.
            print_on_callback (bool, optional): If True, prints progress at each solution callback.
                Defaults to False.
            callback_log_level (int | None, optional): If set to a valid logging level,
                logs the progress message at that level.
                Defaults to None.
        """
        super().__init__()

        if e_timer is None:
            e_timer = ElapsedTimer()
            e_timer.set_start_time_as_now()
        self._e_timer = e_timer
        """Elapsed timer to track the time. If None, a new ElapsedTimer is created and started."""

        self.print_on_callback = print_on_callback
        """If True, prints progress on each solution callback."""

        self.callback_log_level = callback_log_level
        """If set, logs progress at the specified logging level."""

        self.elapsed_time_and_value: list[tuple[float, float]] = []
        """A list of tuples containing (elapsed time, objective value)."""

    def on_solution_callback(self) -> None:
        """
        Called by the solver at each solution.

        - Records the current objective value and elapsed time.
        - Prints progress if print_on_callback is True.
        - Logs progress if callback_log_level is set to a valid logging level.
        """
        elapsed_sec = self._e_timer.elapsed_sec
        obj_value = self.objective_value
        self.elapsed_time_and_value.append((elapsed_sec, obj_value))

        obj_bound = self.best_objective_bound
        info_str = (
            f"Elapsed: {elapsed_sec:.2f} sec, "
            f"Obj. value: {obj_value}, "
            f"Obj. bound: {obj_bound}"
        )
        if self.print_on_callback:
            print(info_str)
        if (
            self.callback_log_level is not None
            and 10 <= self.callback_log_level <= 50
            and self.callback_log_level in logging._levelToName
        ):
            logging.log(self.callback_log_level, info_str)
