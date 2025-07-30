from pathlib import Path

from mbls.cpsat import ObjValueBoundStore

from .time_series_plotter import TimeSeriesPlotter


class ObjValueBoundPlotter:
    """
    Plot the objective value and bound stored in ObjValueBoundStore.
    It utilizes TimeSeriesPlotter to render time series plots.
    """

    @staticmethod
    def plot(
        store: ObjValueBoundStore,
        save_path: Path,
        show_markers: bool = True,
        drop_first_values_percent: float = 0.0,
        title: str = "Objective Value and Bound Over Time",
        xlabel: str = "Elapsed Time (seconds)",
        ylabel: str = "Objective",
        legend_loc: str = "upper right",
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        show: bool = False,
        dpi: int = 300,
        obj_value_label: str = "ObjValue",
        obj_bound_label: str = "ObjBound",
        obj_value_linestyle: str = "-",
        obj_bound_linestyle: str = "--",
    ):
        """Plot the objective value and bound from the given store.

        Args:
            store (ObjValueBoundStore): The store containing the time series.
            save_path (Path): File path to save the plot image.
            show_markers (bool, optional): Whether to show dots on step points.
                Defaults to True.
            drop_first_values_percent (float, optional): Drop early fraction of values (e.g. 0.01 for 1%).
                Defaults to 0.0.
            title (str, optional): Plot title.
                Defaults to "Objective Value and Bound Over Time".
            xlabel (str, optional): X-axis label.
                Defaults to "Elapsed Time (seconds)".
            ylabel (str, optional): Y-axis label.
                Defaults to "Objective".
            legend_loc (str, optional): Legend location.
                Defaults to "upper right".
            xlim (tuple[float, float] | None, optional): X-axis limits.
                Defaults to None.
            ylim (tuple[float, float] | None, optional): Y-axis limits.
                Defaults to None.
            show (bool, optional): Whether to display the plot interactively.
                Defaults to False.
            dpi (int, optional): DPI for saved figure.
                Defaults to 300.
        """
        # Get time series
        obj_value_log = store.obj_value_series.items()
        obj_bound_log = store.obj_bound_series.items()

        lists_of_time_and_val = []
        labels: list[str] = []
        linestyles: list[str] = []

        if obj_value_log:
            lists_of_time_and_val.append(obj_value_log)
            labels.append(obj_value_label)
            linestyles.append(obj_value_linestyle)

        if obj_bound_log:
            lists_of_time_and_val.append(obj_bound_log)
            labels.append(obj_bound_label)
            linestyles.append(obj_bound_linestyle)

        note_map_val = store.obj_value_series.timestamp_note_map
        note_map_bound = store.obj_bound_series.timestamp_note_map
        maps_of_time_to_note = [note_map_val, note_map_bound]

        TimeSeriesPlotter.plot_lists_of_time_and_val(
            lists_of_time_and_val=lists_of_time_and_val,
            save_path=save_path,
            maps_of_time_to_note=maps_of_time_to_note,
            linestyles=linestyles,
            show_markers=show_markers,
            labels=labels,
            drop_first_values_percent=drop_first_values_percent,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend_loc=legend_loc,
            xlim=xlim,
            ylim=ylim,
            show=show,
            dpi=dpi,
        )
