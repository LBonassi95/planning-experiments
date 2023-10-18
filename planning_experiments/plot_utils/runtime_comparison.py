from matplotlib import pyplot as plt
from planning_experiments.summary import *
from typing import Tuple
import numpy as np


class RuntimeComparisonPlot:
    def __init__(
        self, timeout=1800, fontsize=12, plot_kwargs={}, legend_kwargs={}
    ) -> None:
        self.timeout = timeout
        self.fontsize = fontsize
        self.legend_kwargs = legend_kwargs
        self.plot_kwargs = plot_kwargs
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
        self, df: pd.DataFrame, system1: str, system2: str, output_folder: str = None
    ) -> None:
        plt.figure(figsize=(6, 4), dpi=100, facecolor="w", edgecolor="k")
        ax = plt.gca()
        legend = []
        plt.yscale("log")
        plt.xscale("log")
        x = np.geomspace(1e0, self.timeout, num=100)
        points_above = 0
        merged_df, rt_label_1, rt_label_2 = self._extract_systems_dataframes(
            df, system1, system2
        )

        for domain in set(df[DOM]):
            legend.append(domain)
            df_domain = merged_df[merged_df[DOM] == domain]

            rt_1 = list(df_domain[rt_label_1].replace(np.Inf, self.timeout))
            rt_2 = list(df_domain[rt_label_2].replace(np.Inf, self.timeout))

            plt.scatter(rt_1, rt_2, **self.plot_kwargs)
            points_above += len([k for k in np.subtract(rt_2, rt_1) if k > 0])

        print(f"Points above the line: {points_above}")
        plt.plot(x, x, "k--", label="_nolegend_")
        self._show_plot(ax, legend, system1, system2, output_folder)

    def _show_plot(
        self,
        ax: plt.Axes,
        legend: list,
        system1: str,
        system2: str,
        output_folder: str = None,
    ) -> None:
        ax.set_xlabel(f"{system1} runtime", fontsize=self.fontsize)
        ax.set_ylabel(f"{system2} runtime", fontsize=self.fontsize)
        plt.xticks(fontsize=self.fontsize)
        plt.yticks(fontsize=self.fontsize)
        ax.legend(legend, **self.legend_kwargs)
        plt.grid()
        plt.show() if output_folder is None else plt.savefig(
            output_folder / f"{system1}_vs_{system2}.png"
        )
        plt.close()
