from planning_experiments.summary import *
from typing import Tuple
import numpy as np
from planning_experiments.plot_utils.utils import *


class RuntimeComparisonPlot:
    def __init__(
        self, 
        show_axis_labels: bool = True,
        timeout: int = 1800, 
        fontsize: int = 12, 
        hide_legend: bool = False,
        plot_kwargs: dict = {}, 
        legend_kwargs: dict = {}, 
        markers_styles: dict = {}, 
        markers_colors: dict = {},
        domain_legend: dict = {},
        system_legend: dict = {}

    ) -> None:
        self.show_axis_labels = show_axis_labels
        self.timeout = timeout
        self.fontsize = fontsize
        self.legend_kwargs = legend_kwargs
        self.plot_kwargs = plot_kwargs
        self.markers_styles = markers_styles
        self.markers_colors = markers_colors
        self.domain_legend = domain_legend
        self.system_legend = system_legend
        self.hide_legend = hide_legend

        self._color_index = 0

        self._set_kwargs_defaults()

    def _set_kwargs_defaults(self) -> None:
        if "fontsize" not in self.legend_kwargs:
            self.legend_kwargs["fontsize"] = self.fontsize

    def _extract_systems_dataframes(
        self, df: pd.DataFrame, system1: str, system2: str
    ) -> Tuple[pd.DataFrame, str, str]:
        df.loc[df[SOL] == False, RT] = self.timeout
        df = df.drop(columns=[SOL])
        runtime1 = f"{RT}_{system1}"
        runtime2 = f"{RT}_{system2}"
        df_system1 = df[df[SYS] == system1].rename(columns={RT: runtime1})
        df_system2 = df[df[SYS] == system2].rename(columns={RT: runtime2})
        return pd.merge(df_system1, df_system2, on=[DOM, PROB]), runtime1, runtime2

    def plot(
        self, df: pd.DataFrame, system1: str, system2: str, output_path: str = None
    ) -> None:
        plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")
        ax = plt.gca()
        legend = []
        plt.yscale("log")
        plt.xscale("log")
        x = np.geomspace(1e0, self.timeout, num=100)
        points_above = 0
        points_below = 0
        points_on = 0
        merged_df, rt_label_1, rt_label_2 = self._extract_systems_dataframes(
            df, system1, system2
        )

        for domain in set(df[DOM]):
            legend.append(get_legend_entry(self.domain_legend, domain))
            df_domain = merged_df[merged_df[DOM] == domain]

            rt_1 = list(df_domain[rt_label_1].replace(np.Inf, self.timeout))
            rt_2 = list(df_domain[rt_label_2].replace(np.Inf, self.timeout))

            plt.scatter(rt_1, rt_2, marker=get_markers_style(self.markers_styles, domain),
                        color=get_color(self.markers_colors, domain, self._color_index),
                        **self.plot_kwargs)
            self._color_index += 1 # For default colors
            points_above += len([k for k in np.subtract(rt_2, rt_1) if k > 0])
            points_below += len([k for k in np.subtract(rt_2, rt_1) if k < 0])
            points_on += len([k for k in np.subtract(rt_2, rt_1) if k == 0])

        print(f"Points above the line: {points_above}")
        print(f"Points below the line: {points_below}")
        print(f"Points on the line: {points_on}")
        plt.plot(x, x, "k--", label="_nolegend_")
        self._show_plot(ax, legend, system1, system2, output_path)

    def _show_plot(
        self,
        ax: plt.Axes,
        legend: list,
        system1: str,
        system2: str,
        output_path: str = None,
    ) -> None:
        if self.show_axis_labels:
            ax.set_xlabel(f"{get_legend_entry(self.system_legend, system1)} runtime", fontsize=self.fontsize)
            ax.set_ylabel(f"{get_legend_entry(self.system_legend, system2)} runtime", fontsize=self.fontsize)
        plt.xticks(fontsize=self.fontsize)
        plt.yticks(fontsize=self.fontsize)
        if not self.hide_legend:
            ax.legend(legend, **self.legend_kwargs)
        plt.grid()
        plt.show() if output_path is None else plt.savefig(
            output_path, bbox_inches='tight'
        )
        plt.close()

