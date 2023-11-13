from planning_experiments.summary import *
import numpy as np
from planning_experiments.plot_utils.utils import *


class SurvivalPlot:
    def __init__(
        self,
        timeout: int = 1800,
        fontsize: int = 12,
        num_points: int = 1000,
        logscale: bool = False,
        legends_kwargs: dict = {},
        plot_kwargs: dict = {},
        line_colors: dict = {},
        line_styles: dict = {},
        system_legend: dict = {},
    ) -> None:
        self.timeout = timeout
        self.num_points = num_points
        self.logscale = logscale
        self.fontsize = fontsize
        self.legends_kwargs = legends_kwargs
        self.plot_kwargs = plot_kwargs
        self.line_colors = line_colors
        self.line_styles = line_styles
        self.system_legend = system_legend

        self._color_index = 0

    def plot(self, df: pd.DataFrame, output_path: str = None) -> None:
        df = df[df[SOL] == True]
        plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")

        if self.logscale:
            x = np.linspace(1, self.timeout, num=self.num_points)
            plt.xscale("log")
        else:
            x = np.linspace(1, self.timeout, num=self.num_points)

        legend = []
        systems = set(df[SYS])
        df = df[df[SOL] == True]

        for system in systems:
            legend.append(get_legend_entry(self.system_legend, system))
            df_system = df[df[SYS] == system]
            y = np.zeros(len(x))
            runtimes = list(df_system[RT])
            for i in range(len(x)):
                current_time = x[i]
                y[i] = len([r for r in runtimes if r <= current_time])

            plt.plot(x, y, antialiased=True, label=system, color=get_color(self.line_colors, system, self._color_index), 
                     linestyle=get_linestyle(self.line_styles, system), **self.plot_kwargs)
            
            self._color_index += 1 # For default colors

        plt.grid()
        plt.legend(legend, fontsize=self.fontsize, **self.legends_kwargs)
        plt.xlabel(r"Planning time", fontsize=self.fontsize)
        plt.ylabel(r"Coverage", fontsize=self.fontsize)
        plt.show() if output_path is None else plt.savefig(
            output_path, bbox_inches='tight'
        )
        plt.close()
